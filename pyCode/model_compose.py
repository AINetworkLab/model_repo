import pickle
import os
import torch
from collections import OrderedDict

def read(file_path):
    model_shape = {}
    model_hash = {}
    
    with open(file_path, 'r') as file:
        for line in file:
            state = line[1]
            line = line[3:]
            line = line.strip()
            parts = line.split(':')
            layer = parts[0]
            # print(f"layer name is {layer}.")
            data = parts[1][1:-1].split(',')
            match state:
                case 's':#shape
                    layer_shape = []
                    for i in data:
                        layer_shape.append(int(i))
                    model_shape[layer] = layer_shape
                
                case 'p':#parameters
                    hash_value = []
                    for i in data:
                        hash_value.append(i.strip()[1:-1])
                    model_hash[layer] = hash_value

                # print(f"{layer} : {layer_shape}.")
                # for i in range(len(has_value)):
                #     has_value[i] = has_value[i][2:-2]
                # print(f"hash value are {has_value}.")
    return model_shape, model_hash
    
                
def compose(hash_set, data_path):
    # model_name = os.path.splitext(os.path.basename(file_path))[0]
    # _, model_hash = read(file_path)
    model_state = {}
    for k,v in hash_set.items():
        dp = os.path.join(data_path, v +".pkl")
        with open(dp,"rb") as file:
            layer_tensor = pickle.load(file)
        model_state[k] = layer_tensor
    model_state = OrderedDict(model_state)
    return model_state
    # torch.save(model_state,"../"+model_name+"_compose"+".pt")

def get_hash(file_path):
    hash_value = []
    with open(file_path, 'r') as file:
        for line in file:
            state = line[1]
            line = line[3:]
            line = line.strip()
            parts = line.split(':')
            layer = parts[0]
            # print(f"layer name is {layer}.")
            data = parts[1][1:-1].split(',')
            match state:
                case 'p':
                    for i in data:
                        hash_value.append(i.strip()[1:-1])
    return hash_value

def test():
    data_path = "../block_files/speech_recognition/pickle"
    loaded_model_path = "../pytorch_model.txt"
    compose(loaded_model_path, data_path)


if __name__ == "__main__":
    test()