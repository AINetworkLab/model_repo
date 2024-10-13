import hashlib
import os

def hash_file(file_path, output_file):
    """计算单个文件的 SHA-256 哈希值"""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
                
        file_size = os.path.getsize(file_path)
        output_file.write(f"Processed file: {file_path} with hash {sha256.hexdigest()}, size: {file_size} bytes\n")
        
    except PermissionError:
        print(f"Permission denied: {file_path}")
    return sha256.hexdigest()

def hash_directory(directory, output_file):
    """计算文件夹的哈希值并将结果写入文件"""
    sha256 = hashlib.sha256()
    
    try:
        for root, dirs, files in os.walk(directory):
            for names in sorted(dirs + files):
                path = os.path.join(root, names)
                
                # 如果是文件，计算文件哈希
                if os.path.isfile(path):
                    hash_file(path, output_file)
                    
                # 如果是目录，则更新目录路径
                elif os.path.isdir(path):
                    sha256.update(names.encode())
                    # print(f"Processed directory: {path}")
    except PermissionError:
        print(f"Permission denied: {directory}")
        
    return sha256.hexdigest()

# 需要计算哈希值的文件夹列表
directories = [
    '/var/lib/docker/overlay2/a4e58ce122964a02ec8af760effdc0f8cfa57215f10d1e98d822eac33da083cd/diff',
    '/var/lib/docker/overlay2/6a5ae76a42083162f09d251681b761c32ab446a98115879d0256187d4c17cfff/diff',
    '/var/lib/docker/overlay2/6e3031a4cb76d7373f1edf8ab9fa767c6eeff128926e61e420f0ef4b34a7af26/diff',
    '/var/lib/docker/overlay2/541d6345d5956e386a6f9f9a7f392e17103e2e5a803077a0efed43cb136241e5/diff',
    '/var/lib/docker/overlay2/7e0e73bbcee4a64c2ab9b77aac3411986f0c5b2afb04ed4f4a7668ecd0410938/diff',
    '/var/lib/docker/overlay2/1cc1ca16ff7696fe7269977f537d7ebfa0deeef31813333689de5cd9d4df7d65/diff',
    '/var/lib/docker/overlay2/a7abc557d37e2261bd5bc4e19a45bfae3b08a3561242aa42811f0bd00c53b957/diff',
    '/var/lib/docker/overlay2/bcdb35cc946ba9170186aa953c2516f10da2708f8723b3402ae5af88e800d3d1/diff',
    '/var/lib/docker/overlay2/59b00642759565e52ab8831d8781d94a5f52a3db5ec3224d6a1eb652e2309f47/diff',
]

# 打开文件准备写入输出
with open('arm64_output.txt', 'w') as output_file:
    # 计算并打印每个文件夹的哈希值
    for directory in directories:
        folder_hash = hash_directory(directory, output_file)
        # output_file.write(f'The hash of the directory {directory} is: {folder_hash}\n')
