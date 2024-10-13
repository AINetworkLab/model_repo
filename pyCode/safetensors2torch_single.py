import torch
from safetensors.torch import load_file

# 加载 safetensors 文件
file_path = "/home/wangsheng/Downloads/model-00002-of-00007.safetensors"
tensors = load_file(file_path)

# 创建一个字典来存储加载的张量
state_dict = {k: v for k, v in tensors.items()}

# 保存为 .pt 文件
output_path = "/home/wangsheng/Downloads/model-00002-of-00007.bin"
torch.save(state_dict, output_path)

print(f"模型已保存为 {output_path}")
