import hashlib
import os

def hash_file(file_path):
    """计算单个文件的 SHA-256 哈希值"""
    sha256 = hashlib.sha256()
    file_size = os.path.getsize(file_path)
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
    except PermissionError:
        print(f"Permission denied: {file_path}")
    return sha256.hexdigest(), file_size

def hash_directory(directory, output_file):
    """计算文件夹的哈希值并将结果写入文件"""
    sha256 = hashlib.sha256()
    
    try:
        for root, dirs, files in os.walk(directory):
            for names in sorted(dirs + files):
                path = os.path.join(root, names)
                
                # 如果是文件，计算文件哈希
                if os.path.isfile(path):
                    file_hash, file_size = hash_file(path)
                    sha256.update(file_hash.encode())
                    output_file.write(f"Processed file: {path} with hash {file_hash}, size: {file_size} bytes\n")
                    
                # 如果是目录，则更新目录路径
                elif os.path.isdir(path):
                    sha256.update(names.encode())
                    # print(f"Processed directory: {path}")
    except PermissionError:
        print(f"Permission denied: {directory}")
        
    return sha256.hexdigest()

# 需要计算哈希值的文件夹列表
directories = [
    '/var/lib/docker/overlay2/3c595fbec79b4128c3efbb2c2dc1988615d36eca857b69c81a0d6f56b93ab057/diff',
    '/var/lib/docker/overlay2/e499e6abf25d8cfe4781eda1449cd210c4e95d1b51a2f714e542191e33b7c1d7/diff',
    '/var/lib/docker/overlay2/a6bdfefe523d90aca918a4f77c9283d324bfe9af5b22c66928e14aa2fa6c7467/diff',
    '/var/lib/docker/overlay2/529fe3d923f51a8dd3dfef231487128baf2b0981edaa3109b2e1def7e25b16ec/diff',
    '/var/lib/docker/overlay2/c07efde795992835ae565b4038584118e64aa1b6f5d95a28d48c3963210244fe/diff',
    '/var/lib/docker/overlay2/fea21edcf4e407dc4d45eb5ec59a2dffcb952d9ff6397ceadbd572e97087a753/diff',
    '/var/lib/docker/overlay2/5897a9738141c5b93fe128d512e624bc37923b16d15f91d209628fc5102cdf49/diff',
    '/var/lib/docker/overlay2/9ad7dc0de03798d4523f3f597160aa9a8d0dad2a8573098a77229a2e9acd3434/diff',
    '/var/lib/docker/overlay2/a568120f96003e03763db4be23ac9b1b95763a930d637d78959e7e68468885e4/diff',
]

# 打开文件准备写入输出
with open('amd64_output.txt', 'w') as output_file:
    # 计算并打印每个文件夹的哈希值
    for directory in directories:
        folder_hash = hash_directory(directory, output_file)
        # output_file.write(f'The hash of the directory {directory} is: {folder_hash}\n')
