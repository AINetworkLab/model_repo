import storage_dao
import data_dao
import model_dao
import os
from temp_dir import TempDir
import minio_utils as utils
import torch
from entity import ModelInfo, StorageInfo, DataInfo, ModelInfo_2, LocationInfo
from fastapi import FastAPI, UploadFile, BackgroundTasks
import model_compose
from starlette.responses import FileResponse
from concurrent.futures import ThreadPoolExecutor, as_completed

import time

def timeit_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {execution_time} seconds")
        return result
    return wrapper

# start_time = time.time()
# your_function()
# end_time = time.time()

# execution_time = end_time - start_time
# print(f"Function execution time: {execution_time} seconds")

def remove_file(model_path: str):
    if model_path and os.path.exists(model_path):
        os.remove(model_path)

def get_directory_size(directory_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

async def upload(file: UploadFile):
    put_time = 0
    db_time = 0
    file_name = file.filename
    obj_name_prefix = os.path.splitext(file_name)[0]
    minio_size_all = 0
    unre_size_all = 0
    try:
        file_loaded = 0
        minio_count = 0
        disk_spaces = {}
        
        with TempDir() as tmp:
            base_path = tmp.path()
            file_path = os.path.join(base_path, file_name)
            model_path = os.path.join(base_path, "model")
            # 将上传文件内容写入本地文件
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            model_size_all = os.path.getsize(file_path)
            print(f"模型 {obj_name_prefix} 的大小为：{model_size_all} 字节")
            print(f"模型 {obj_name_prefix} 的大小为：{model_size_all/1024/1024} MB")
            # print(file_path)
            loaded_model_state = torch.load(file_path, map_location='cpu')
            # print(loaded_model_state)
            #这里把hash表变成二维的，使其能够存储模型内冗余层数量
            layer_name_list, layer_hash_list = utils._save_state_dict(state_dict=loaded_model_state, path=model_path)
            # 获取文件夹下的所有文件并获取文件数量
            files = list(os.scandir(model_path))
            unre_size_all = get_directory_size(model_path)
            print(f"去除冗余后的模型 {obj_name_prefix} 的大小为：{unre_size_all} 字节")
            print(f"去除冗余后的模型 {obj_name_prefix} 的大小为：{unre_size_all/1024/1024} MB")
            file_num = len(files)
            
            times_for_db = 0
            times_for_storage = 0
            
            for layer_hash in layer_hash_list:
                print("layer_hash: ", layer_hash)
                # layer_hash = layer_hash[0]
                file_loaded += 1
                # print(isinstance(layer_hash, str))
                # print(layer_hash)
                #判断模型是否存在
                tmp_models = model_dao.get_model_by_layer_hash_all(layer_hash)
                # 模型不存在
                if len(tmp_models) == 0:
                    disks = storage_dao.get_storage_all()
                    for disk in disks:
                        key = disk.minio_id + "_" + disk.minio_location
                        value = disk.free_space
                        disk_spaces[key] = value
                    file_size = os.path.getsize(model_path + "/" + layer_hash + ".pkl")
                    minio_id = utils.get_disk(file_size, disk_spaces)
                    if minio_id == "-1":
                        sql_data = DataInfo(model_name=obj_name_prefix, file_number=file_num,
                                            layer_number=len(layer_hash_list), minio_count=minio_count, complete=0)
                        data_dao.add_data(sql_data)
                        return {"error": "无可用磁盘", "file_num": file_num, "file_loaded": file_loaded - 1,
                                "layer_hash_len": len(layer_hash_list),
                                "minio_count": minio_count}
                    client = utils.get_client(minio_id)
                    start = time.time()*1000
                    client.fput_object(bucket_name="test", object_name=obj_name_prefix + "/" + layer_hash + ".pkl",
                                       file_path=model_path + "/" + layer_hash + ".pkl")
                    end = time.time()*1000
                    put_time +=(end-start)
                    storage = storage_dao.get_storage_by_minio_id(minio_id)
                    storage_dao.update_used_storage(file_size=file_size, storage=storage, minio_id=minio_id)
                    minio_count += 1
                    minio_size_all += file_size

                    # round(file_size / (1024 * 1024), 2)
                    
                    db_model = ModelInfo(layer_hash=layer_hash, model_name=obj_name_prefix, minio_id=minio_id,
                                         layer_number=file_loaded, layer_name=layer_name_list[file_loaded - 1],
                                         layer_location=obj_name_prefix,layer_size = file_size)
                    model_dao.add_model(db_model)
                else:
                    start = time.perf_counter()*1000
                    for tmp_model in tmp_models:
                        db_model = ModelInfo(layer_hash=tmp_model.layer_hash, model_name=obj_name_prefix,
                                             minio_id=tmp_model.minio_id, layer_number=file_loaded,
                                             layer_name=layer_name_list[file_loaded - 1],layer_location=tmp_model.layer_location,layer_size = tmp_model.layer_size)
                        existing_models = model_dao.existing_models(db_model)
                        if len(existing_models) == 0:
                            model_dao.add_model(db_model)
                    end = time.perf_counter()*1000
                    db_time +=(end-start)
        sql_data = DataInfo(model_name=obj_name_prefix, file_number=file_num, layer_number=len(layer_hash_list),
                            minio_count=minio_count, complete=1)
        data_dao.add_data(sql_data)
        print(f"模型 {obj_name_prefix} 存储在 minio 中的总大小为：{minio_size_all} 字节")
        print(f"模型 {obj_name_prefix} 存储在 minio 中的总大小为：{minio_size_all/1024/1024} MB")
        return {"file_num": file_num, "file_loaded": file_loaded, "layer_hash_len": len(layer_hash_list),
                "minio_count": minio_count,"put_time":put_time,"db_time":db_time,"total_time":put_time+db_time}
    except Exception as e:
        print("文件存储异常: ", e)
        return {"error": "文件存储异常: " + str(e)}

async def upload_(file: UploadFile):
    put_time = 0
    db_time = 0
    file_name = file.filename
    obj_name_prefix = os.path.splitext(file_name)[0]
    try:
        file_loaded = 0
        minio_count = 0
        disk_spaces = {}
        
        with TempDir() as tmp:
            base_path = tmp.path()
            file_path = os.path.join(base_path, file_name)
            model_path = os.path.join(base_path, "model")
            # 将上传文件内容写入本地文件
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            loaded_model_state = torch.load(file_path, map_location='cpu')
            # print(loaded_model_state)
            layer_name_list, layer_hash_list = utils._save_state_dict(state_dict=loaded_model_state, path=model_path)
            # 获取文件夹下的所有文件并获取文件数量
            files = list(os.scandir(model_path))
            file_num = len(files)
            
            times_for_db = 0
            times_for_storage = 0
            
            for layer_hash in layer_hash_list:
                file_loaded += 1
                #判断模型是否存在
                tmp_models = model_dao.get_model_by_layer_hash(layer_hash)
                if len(tmp_models) == 0:
                    disks = storage_dao.get_storage_all()
                    for disk in disks:
                        key = disk.minio_id + "_" + disk.minio_location
                        value = disk.free_space
                        disk_spaces[key] = value
                    file_size = os.path.getsize(model_path + "/" + layer_hash + ".pkl")
                    minio_id = utils.get_disk(file_size, disk_spaces)
                    if minio_id == "-1":
                        sql_data = DataInfo(model_name=obj_name_prefix, file_number=file_num,
                                            layer_number=len(layer_hash_list), minio_count=minio_count, complete=0)
                        data_dao.add_data(sql_data)
                        return {"error": "无可用磁盘", "file_num": file_num, "file_loaded": file_loaded - 1,
                                "layer_hash_len": len(layer_hash_list),
                                "minio_count": minio_count}
                    client = utils.get_client(minio_id)
                    start = time.time()*1000
                    client.fput_object(bucket_name="test", object_name=obj_name_prefix + "/" + layer_hash + ".pkl",
                                       file_path=model_path + "/" + layer_hash + ".pkl")
                    end = time.time()*1000
                    put_time +=(end-start)
                    storage = storage_dao.get_storage_by_minio_id(minio_id)
                    storage_dao.update_used_storage(file_size=file_size, storage=storage, minio_id=minio_id)
                    minio_count += 1
                    # db_model = ModelInfo(layer_hash=layer_hash, model_name=obj_name_prefix, minio_id=minio_id,
                    #                      layer_number=file_loaded, layer_name=layer_name_list[file_loaded - 1],
                    #                      layer_location=obj_name_prefix)
                    db_model_2 = ModelInfo_2(model_name=obj_name_prefix, layer_num=file_loaded, layer_hash=layer_hash,
                    layer_name=layer_name_list[file_loaded - 1])
                    model_dao.add_model_2(db_model_2)
                    db_location = LocationInfo(layer_hash=layer_hash, layer_location=obj_name_prefix, minio_id=minio_id)
                    model_dao.add_location(db_location)
                    
                else:
                    start = time.perf_counter()*1000
                    
                    for tmp_model in tmp_models:

                        # db_model = ModelInfo(layer_hash=tmp_model.layer_hash, model_name=obj_name_prefix,
                        #                      minio_id=tmp_model.minio_id, layer_number=file_loaded,
                        #                      layer_name=layer_name_list[file_loaded - 1],layer_location=tmp_model.layer_location)
                        db_model_2 = ModelInfo_2(model_name=obj_name_prefix, layer_num=file_loaded, layer_hash=layer_hash,
                                             layer_name=layer_name_list[file_loaded - 1])
                        existing_models = model_dao.existing_models_2(db_model_2)
                        if len(existing_models) == 0:
                            model_dao.add_model_2(db_model_2)
                    end = time.perf_counter()*1000
                    db_time +=(end-start)
        sql_data = DataInfo(model_name=obj_name_prefix, file_number=file_num, layer_number=len(layer_hash_list),
                            minio_count=minio_count, complete=1)
        data_dao.add_data(sql_data)
        return {"file_num": file_num, "file_loaded": file_loaded, "layer_hash_len": len(layer_hash_list),
                "minio_count": minio_count,"put_time":put_time,"db_time":db_time,"total_time":put_time+db_time}
    except Exception as e:
        print("文件存储异常: ", e)
        return {"error": "文件存储异常: " + str(e)}




async def download(model_name: str, background_task: BackgroundTasks):
    total_time=0
    try:
        hash_set = {}
        model = sorted(model_dao.get_model_by_model_name(model_name), key=lambda x: x.layer_number)
        # 文件夹路径
        folder_path = "/tmp/model"
        # 检查文件夹是否存在，如果不存在则创建
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        model_path = os.path.join(folder_path, model_name + ".pt")
        if model is None:
            return {"error": "模型不存在"}
        with TempDir() as tmp:
            base_path = tmp.path()
            for layer in model:
                hash_set[layer.layer_name] = layer.layer_hash
                idx = layer.minio_id
                client = utils.get_client(idx)
                start = time.perf_counter()*1000
                client.fget_object(bucket_name="test", object_name=layer.layer_location + "/" + layer.layer_hash + ".pkl",
                                   file_path=os.path.join(base_path, layer.layer_hash + ".pkl"))
                end = time.perf_counter()*1000
                total_time += (end-start)
            state_dict = model_compose.compose(hash_set, base_path)
            torch.save(state_dict, model_path)
        background_task.add_task(remove_file, model_path)
        
        print("time: "+str(total_time)+"ms")
        return FileResponse(model_path, media_type="application/octet-stream", filename=model_name + '.pt')
    except Exception as e:
        print("文件下载异常: ", e)
        return {"error": "文件下载异常: " + str(e)}

async def download_(model_name: str, background_task: BackgroundTasks):
    total_time=0
    try:
        hash_set = {}
        model = sorted(model_dao.get_model_by_model_name_2(model_name), key=lambda x: x.layer_num)
        # 文件夹路径
        folder_path = "/tmp/model"
        # 检查文件夹是否存在，如果不存在则创建
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        model_path = os.path.join(folder_path, model_name + ".pt")
        if model is None:
            return {"error": "模型不存在"}
        with TempDir() as tmp:
            base_path = tmp.path()
            # hash_set = get_hash_set(model)
            for layer in model:
                hash_set[layer.layer_name] = layer.layer_hash
                #idx_set[layer.layer_hash] = get_minio_id(layer.layer_hash)
                #idx = layer.minio_id
                # layer_location = get_minio_id(layer.layer_hash)
                layer_location = "1"
                idx = layer_location.minio_id
                client = utils.get_client(idx)
                start = time.perf_counter()*1000
                client.fget_object(bucket_name="test", object_name=layer_location.layer_location + "/" + layer.layer_hash + ".pkl",
                                   file_path=os.path.join(base_path, layer.layer_hash + ".pkl"))
                end = time.perf_counter()*1000
                total_time += (end-start)
            state_dict = model_compose.compose(hash_set, base_path)
            torch.save(state_dict, model_path)
        background_task.add_task(remove_file, model_path)
        
        print("time: "+str(total_time)+"ms")
        return FileResponse(model_path, media_type="application/octet-stream", filename=model_name + '.pt')
    except Exception as e:
        print("文件下载异常: ", e)
        return {"error": "文件下载异常: " + str(e)}


async def delete_all():
    try:
        # 删除 model表中的所有数据
        model_dao.delete_all()
        # 删除 data表中的所有数据
        data_dao.delete_all()
        # 删除 test 桶的中的所有对象
        for i in range(1, 5):
            client = utils.get_client(str(i))
            objects = client.list_objects("test", prefix="", recursive=True)
            for obj in objects:
                client.remove_object("test", obj.object_name)
        # 更新 storage
        storage_dao.refresh_storage()
        return {"result ": "删除成功！"}
    except Exception as e:
        return {"error": str(e)}

async def delete_all_2():
    try:
        # 删除 model表中的所有数据
        model_dao.delete_all_2()
        # 删除 data表中的所有数据
        data_dao.delete_all()
        # 删除 test 桶的中的所有对象
        for i in range(1, 5):
            client = utils.get_client(str(i))
            objects = client.list_objects("test", prefix="", recursive=True)
            for obj in objects:
                client.remove_object("test", obj.object_name)
        # 更新 storage
        storage_dao.refresh_storage()
        return {"result ": "删除成功！"}
    except Exception as e:
        return {"error": str(e)}        
    
# async def delete_by_model_name(model_name:str):
#     try:           
#         # 删除 model表中的所有数据
#         model_dao.delete_by_model_name(model_name)
#         # 删除 data表中的所有数据
#         data_dao.delete_by_model_name(model_name)
#         # 删除 test 桶的中的所有对象
#         for i in range(1, 5):
#             client = utils.get_client(str(i))
#             objects = client.list_objects("test", prefix=model_name, recursive=True)
#             for obj in objects:
#                 client.remove_object("test", obj.object_name)
#         # 更新 storage
#         storage_dao.refresh_storage()
#         return {"result ": "删除成功！"}
#     except Exception as e:
#         return {"error": str(e)}