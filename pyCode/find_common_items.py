import torch
import hashlib
from collections import defaultdict
from itertools import chain

def hash_cal(weights):
    block = weights.cpu().numpy()
    block_hash = hashlib.sha256(block.tobytes()).hexdigest()
    return block_hash

def find_common_items(hash_lists):
    # 使用 itertools.chain 合并所有列表的项目
    merged_list = list(chain(*hash_lists))
    
    # 字典用于统计每个项目在每个列表中出现的次数
    item_count = defaultdict(int)
    
    # 遍历每个列表
    for hash_list in hash_lists:
        # 使用集合去重，确保每个项目在一个列表中只计数一次
        unique_items = set(hash_list)
        for item in unique_items:
            item_count[item] += 1
    
    # 找出在所有列表中都出现的项目
    common_items = {item: count for item, count in item_count.items() if count == len(hash_lists)}
    
    return common_items

model1 = torch.load("/home/wangsheng/Downloads/A_model_re/timm_resnet50.fb_swsl_ig1b_ft_in1k.bin")
model2 = torch.load("/home/wangsheng/Downloads/A_model_re/timm_resnet50.tv_in1k.bin")
model3 = torch.load("/home/wangsheng/Downloads/A_model_re/timm_resnet50d.ra2_in1k.bin")
model4 = torch.load("/home/wangsheng/Downloads/A_model_re/timm_resnet50.a1h_in1k.bin")
model5 = torch.load("/home/wangsheng/Downloads/A_model_re/timm_wide_resnet50_2.racm_in1k.bin")
model6 = torch.load("/home/wangsheng/Downloads/A_model_re/timm_resnet50.a1_in1k.bin")

model7 = torch.load("/home/wangsheng/Downloads/A_model_re/resnet-50.bin")
model8 = torch.load("/home/wangsheng/Downloads/A_model_re/detr-resnet-50.bin")
model9 = torch.load("/home/wangsheng/Downloads/detr-resnet-50-dc5.bin")
model10 = torch.load("/home/wangsheng/Downloads/detr-resnet-50-dc5-panoptic.bin")

hash_list1 = []
for k,v in model1.items():
    hash_list1.append(hash_cal(v))

hash_list2 = []
for k,v in model2.items():
    hash_list2.append(hash_cal(v))

hash_list3 = []
for k,v in model3.items():
    hash_list3.append(hash_cal(v))

hash_list4 = []
for k,v in model4.items():
    hash_list4.append(hash_cal(v))

hash_list5 = []
for k,v in model5.items():
    hash_list5.append(hash_cal(v))

hash_list6 = []
for k,v in model6.items():
    hash_list6.append(hash_cal(v))

hash_list7 = []
for k,v in model7.items():
    hash_list7.append(hash_cal(v))

hash_list8 = []
for k,v in model8.items():
    hash_list8.append(hash_cal(v))

hash_list9 = []
for k,v in model9.items():
    hash_list9.append(hash_cal(v))

hash_list10 = []
for k,v in model10.items():
    hash_list10.append(hash_cal(v))

# hash_lists=[hash_list1,hash_list2,hash_list3,hash_list4,hash_list5,hash_list6]

# hash_lists=[hash_list7,hash_list6]
# common_items = find_common_items(hash_lists)
# print(common_items)
# print(len(common_items))

# hash_lists=[hash_list8,hash_list2]
# common_items = find_common_items(hash_lists)
# print(common_items)
# print(len(common_items))

# hash_lists=[hash_list8,hash_list1]
# common_items = find_common_items(hash_lists)
# print(common_items)
# print(len(common_items))


hash_lists=[hash_list10,hash_list9]
common_items = find_common_items(hash_lists)
print(common_items)
print(len(common_items))
