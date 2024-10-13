#import h5py
import pickle
import os
import torch
import hashlib
# import detect_model

def hash_cal(weights):
    # print(type(weights))
    # print(weights)
    block = weights.cpu().numpy()
    block_hash = hashlib.sha256(block.tobytes()).hexdigest()
    return block_hash
    

def save_block(block, dirs, meth="pickle", **kwargs):

    if not os.path.exists(dirs):
        os.makedirs(dirs)
    file_path = hash_cal(block)
    # meth_dir = os.path.join(dirs,meth)
    # for k,v in kwargs.items():
    #     if k == "file_list":
    #         file_list = v
    
    # if file_list:
    #     if file_path in file_list:
    #         return
    # if meth == 'hdf5':
    #     # dirs = "./block_files/TEST"
    #     file_name = os.path.join(dirs, file_path+".h5")

    #     if not os.path.exists(file_name):
    #         with h5py.File(file_name, 'w') as hf:
    #             hf.create_dataset('weights', data=block)
            
    if meth == 'pickle':
        file_name = os.path.join(dirs, file_path+".pkl")
        
        if not os.path.exists(file_name):
            with open(file_name, 'wb') as file:
                pickle.dump(block, file)
            
    elif meth == "torch":
        file_name = os.path.join(dirs, file_path+".pt")
        
        # 去除内部冗余
        if not os.path.exists(file_name):
            torch.save(block, file_name)
            
    return file_path
        
# def _save_hash(model_path):
#     file_name = os.path.splitext(os.path.basename(model_path))[0]
#     with open('hash_info.txt', 'w') as file:
#         file.write(f"File: {file_name}, Size: {file_size} bytes, Hash: {hash_value}\n")
    
def save_weights(info_path,layer_name,dirs,weights,block_size=5,dim_used=2):
    weights_shape = {}
    hash_table = []
    for i in range(len(weights.shape)):
        weights_shape[i] = weights.shape[i]
    
    hash_table.append(save_block(weights,dirs))
    
    # match min(dim_used,len(weights_shape)):
    #     case 2:
    #         for i in range(0, weights_shape[0], block_size):
    #             for j in range(0, weights_shape[1], block_size):
    #                 block = weights[i:i+block_size, j:j+block_size]
    #                 hash_table.append(save_block(block, dirs))
    #     case 1:
    #         for i in range(0, weights_shape[0], block_size):
    #             block = weights[i:i+block_size]
    #             hash_table.append(save_block(block, dirs))
                
    # for i in range(0, weights_shape[0], block_size):
    #     for j in range(0, weights_shape[1], block_size):
    #         block = weights[i:i+block_size, j:j+block_size]
    #         hash_table.append(save_block(block, dirs))
                
    with open(info_path, 'a') as file:
        file.write("[p]")
        file.write(f"{layer_name}:{hash_table}\n")
    
def save_model(dirs, loaded_model_path):
    # model_type = detect_model.detect_framework(loaded_model_path)
    # #print(model_type)
    # if model_type != "PyTorch":
    #     raise RuntimeError("非PyTorch模型")
    # if model_type == "Unknown":
    #     raise RuntimeError("未定义模型类型")
    loaded_model_state = torch.load(loaded_model_path)
    info_path = os.path.splitext(os.path.basename(loaded_model_path))[0]+".txt"
    
    #用w即可
    if not os.path.exists(info_path):
        os.mknod(info_path)
    else:
        with open(info_path, 'a+') as file:
            file.truncate(0)
        
    for k,v in loaded_model_state.items():
        with open(info_path, 'a') as file:
            file.write("[s]")
            file.write(f"{k}:{list(v.shape)}\n")
        save_weights(info_path,k,dirs,v)
    
    
def save_info(dirs, state_dict, **kwargs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    info_path = os.path.join(dirs ,"model_info.txt")
    if not os.path.exists(info_path):
        os.mknod(info_path)
    else:
        with open(info_path, 'a+') as file:
            file.truncate(0)
    for k,v in state_dict.items():
        hash_table = []
        hash_table.append(hash_cal(v))
        with open(info_path, 'a') as file:
            file.write("[s]")
            file.write(f"{k}:{list(v.shape)}\n")
            file.write("[p]")
            file.write(f"{k}:{hash_table}\n")
    
def save_state_dict(dirs, state_dict, **kwargs):
    layer_hash = []
    layer_name = []
    for k,v in state_dict.items():
        layer_name.append(k)
        file_path = save_block(block=v, dirs=dirs,**kwargs)
        layer_hash.append(file_path)
    
    return layer_name, layer_hash

# def save_state_dict(dirs, state_dict, **kwargs):
#     layer_hash = []
#     layer_name = []
#     for k,v in state_dict.items():
#         layer_name.append(k)
#         file_path = save_block(block=v, dirs=dirs,**kwargs)
#         for item in layer_hash:
#             if file_path == item[0]:
#                 item[1] += 1
#                 # print(item)
#                 break
#         else:
#             layer_hash.append([file_path,1])
        
#     return layer_name, layer_hash

def test():
    # 假设有一个模型并保存它
    # class MyModel(nn.Module):
    #     def __init__(self):
    #         super(MyModel, self).__init__()
    #         self.layer1 = nn.Linear(10, 20)
    #         self.layer2 = nn.Linear(20, 30)
    #         self.layer3 = nn.Linear(30, 5)
        
    #     def forward(self, x):
    #         x = torch.relu(self.layer1(x))
    #         x = torch.relu(self.layer2(x))
    #         x = self.layer3(x)
    #         return x
    # 加载已保存的模型
    dirs = "../block_files/speech_recognition"
    loaded_model_path = '../pytorch_model.bin'
    save_model(dirs, loaded_model_path)
        
    
if __name__ == "__main__":
    test()