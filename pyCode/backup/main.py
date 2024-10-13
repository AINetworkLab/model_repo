from typing import Union
from fastapi import FastAPI, UploadFile, BackgroundTasks
import torch
from temp_dir import TempDir
import os
import minio_utils as utils
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, text, update
from fastapi.responses import FileResponse
import model_compose
import model_save
import uvicorn
from entity import ModelInfo

app = FastAPI()

# 创建数据库连接
SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:mysql_pwd@localhost:3306/minio?charset=utf8mb4'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建 SessionLocal 类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 Base 类
Base = declarative_base()


class ModelInfo(Base):
    __tablename__ = 'models'

    id = Column(Integer, primary_key=True, index=True)
    layer_hash = Column(String(255), nullable=False)
    model_name = Column(String(255), nullable=False)
    minio_id = Column(String(255), nullable=False)
    layer_number = Column(Integer, nullable=False)
    layer_name = Column(String(255), nullable=False)

class StorageInfo(Base):
    __tablename__ = 'storage'

    minio_id = Column(String(255), primary_key=True, index=True)
    minio_location = Column(String(255), nullable=False)
    used_space = Column(String(255), nullable=False)
    free_space = Column(String(255), nullable=False)
    total_space = Column(String(255), nullable=False)

class DataInfo(Base):
    __tablename__ = 'storage_data'
    model_name = Column(String(255), primary_key=True, index=True)
    file_number = Column(Integer, nullable=False) # 模型去掉自身冗余后的层数
    layer_number = Column(Integer, nullable=False) # 模型的总层数
    minio_count = Column(Integer, nullable=False) # minio存储的层条目数
    sql_count = Column(Integer, nullable=False) # 数据库存储的层条目数


@app.post("/minio/upload", summary="上传文件到minio")
async def upload(file: UploadFile):
    file_name = file.filename
    obj_name_prefix = os.path.splitext(file_name)[0]
    try:
        file_loaded = 0
        file_num = 0
        minio_count = 0
        session = SessionLocal()
        layer_name_list = []
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
            for layer_hash in layer_hash_list:
                file_loaded += 1
                tmp_models = session.query(ModelInfo).filter(ModelInfo.layer_hash == layer_hash).all()
                # print("测试测试："+tmp_model)
                if len(tmp_models) == 0:
                    # TODO: 获取可用磁盘空间
                    disks = session.query(StorageInfo).all()
                    for disk in disks:
                        key = disk.minio_id+"_"+disk.minio_location
                        value = disk.free_space
                        disk_spaces[key] = value
                    file_size = os.path.getsize(model_path + "/" + layer_hash + ".pkl")
                    idx = utils.get_disk(file_size,disk_spaces)
                    if idx == "-1":
                        return {"error": "无可用磁盘","file_num": file_num, "file_loaded": file_loaded-1, "layer_hash_len": len(layer_hash_list),
                "minio_count": minio_count}
                    # TODO: 获取minio client
                    client = utils.get_client(idx)
                    client.fput_object(bucket_name="test", object_name=obj_name_prefix + "/" + layer_hash + ".pkl",
                                       file_path=model_path + "/" + layer_hash + ".pkl")
                    storage = session.query(StorageInfo).filter(StorageInfo.minio_id == idx).first()
                    current_free_space = int(storage.free_space)
                    new_free_space = current_free_space - file_size
                    new_used_space = int(storage.used_space) + file_size
                    stmt = (
                        update(StorageInfo)
                        .where(StorageInfo.minio_id == idx)
                        .values(
                            free_space=str(new_free_space),
                            used_space=str(new_used_space)
                        )
                    )
                    session.execute(stmt)
                    session.commit()
                    # session.refresh(storage)
                    minio_count += 1
                    db_model = ModelInfo(layer_hash=layer_hash, model_name=obj_name_prefix, minio_id=idx,
                                         layer_number=file_loaded, layer_name=layer_name_list[file_loaded - 1])
                    session.add(db_model)
                    session.commit()
                    # session.refresh(db_model)
                else:
                    for tmp_model in tmp_models:
                        # if tmp_model.layer_number != file_loaded and tmp_model.model_name != obj_name_prefix:
                        db_model = ModelInfo(layer_hash=tmp_model.layer_hash, model_name=obj_name_prefix,
                                                minio_id=tmp_model.minio_id, layer_number=file_loaded,
                                                layer_name=layer_name_list[file_loaded - 1])
                        existing_model = session.query(ModelInfo).filter(
        ModelInfo.layer_hash == db_model.layer_hash,
        ModelInfo.model_name == db_model.model_name,
        ModelInfo.minio_id == db_model.minio_id,
        ModelInfo.layer_number == db_model.layer_number,
        ModelInfo.layer_name == db_model.layer_name).first()
                        if existing_model is None:
                            session.add(db_model)
                            session.commit()
                            # session.refresh(db_model)
        sql_data = DataInfo(model_name=obj_name_prefix,file_number=file_num,layer_number=len(layer_hash_list),minio_count=minio_count)
        session.add(sql_data)
        session.commit()
        return {"file_num": file_num, "file_loaded": file_loaded, "layer_hash_len": len(layer_hash_list),
                "minio_count": minio_count}
    except Exception as e:
        print("文件存储异常: ", e)
        return {"error": "文件存储异常: " + str(e)}
    finally:
        session.close()


def remove_file(model_path: str):
    if model_path and os.path.exists(model_path):
        os.remove(model_path)


@app.post("/minio/download", summary="从minio下载")
async def download(model_name: str, background_task: BackgroundTasks):
    model_path = None
    session = SessionLocal()
    try:
        hash_set = {}
        model = session.query(ModelInfo).filter(ModelInfo.model_name == model_name).all()
        model = sorted(model, key=lambda x: x.layer_number)
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
                client.fget_object(bucket_name="test", object_name=layer.model_name + "/" + layer.layer_hash + ".pkl",
                                   file_path=os.path.join(base_path, layer.layer_hash + ".pkl"))
            state_dict = model_compose.compose(hash_set, base_path)
            torch.save(state_dict, model_path)
        background_task.add_task(remove_file, model_path)
        return FileResponse(model_path, media_type="application/octet-stream", filename=model_name + '.pt')
    except Exception as e:
        print("文件下载异常: ", e)
        return {"error": "文件下载异常: " + str(e)}
    finally:
        if session:
            session.close()

@app.post("/minio/delete_all", summary=" 删除所有信息")
async def delete_all():
    # 创建数据库会话
    session = SessionLocal()
    try:
        # 执行 TRUNCATE TABLE 语句
        truncate_sql = text("TRUNCATE TABLE models;")
        session.execute(truncate_sql)
        session.commit()
        sql= text("TRUNCATE TABLE storage_data;")
        session.execute(sql)
        session.commit()
        # 删除 test 桶的中的所有对象
        for i in range(1, 5):
            client = utils.get_client(str(i))
            objects = client.list_objects("test", prefix="", recursive=True)
            for obj in objects:
                client.remove_object("test", obj.object_name)
        # 更新 storage
        s_sql = text("UPDATE storage SET used_space = '0', free_space = total_space;")
        session.execute(s_sql)
        session.commit()
        return {"result ":"删除成功！"}
    except Exception as e:
        # 回滚事务在异常情况下
        session.rollback()
        return {"error":e}
    finally:
        # 关闭会话
        session.close()

# @app.post("/minio/delete", summary="根据 model_name 删除信息")
# async def delete():
#    pass


if __name__ == "__main__":
    uvicorn.run(app='main:app', host='0.0.0.0', port=8000, reload=True)

