import torch
from safetensors.torch import load_file

base_path = "/home/wangsheng/Downloads/"

# 假设有多个 safetensors 文件
file_paths = [
    base_path+"model-00001-of-00002.safetensors",
    base_path+"model-00002-of-00002.safetensors",
]

# 创建一个字典来存储所有加载的张量
state_dict = {}

# 加载并合并所有 safetensors 文件
for file_path in file_paths:
    tensors = load_file(file_path)
    state_dict.update(tensors)

# 保存为 .pt 文件
output_path = base_path+"openbmb_MiniCPM-Llama3-V-2_5-int4.bin"
torch.save(state_dict, output_path)

print(f"模型已保存为 {output_path}")
