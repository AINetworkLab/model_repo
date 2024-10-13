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
    '/var/lib/docker/overlay2/7fa593ed5627fb3cbf1f91444b4df13e4cf14700a63639b508f7f9eb8d151f91/diff',
    '/var/lib/docker/overlay2/201add3e7fad59bda7aa39e8856a78fe3faba5b5a925bfdb11f92aa52446e038/diff',
    '/var/lib/docker/overlay2/340ffaf8d50f2276b3630df7ef04107263b664fa3695cddf2d690bbc3660b1b5/diff',
    '/var/lib/docker/overlay2/487c26a3f082f031651e8dd06af8545c5d6ddf740f4fe72d04fa431c184d0fc9/diff',
    '/var/lib/docker/overlay2/aad3bcab83254be057703ead80527c09ec8d20ea693adc7c4b13c0e4f75df837/diff',
    '/var/lib/docker/overlay2/b06228fd32a263d1b18af3abac2cf72643dfcb96ecaa19239c0229fc6ddbc7a8/diff',
    '/var/lib/docker/overlay2/064c2850d0261e24102f2c82ce9bcd11491755634fc812ae13318b7321dbb0b0/diff',
    '/var/lib/docker/overlay2/ebdbd2739dd9dd1ce8779cdd7b8789cfb3df79473386a83b8af87a92cc107369/diff',
    '/var/lib/docker/overlay2/9d0ab7e950491e9680e02d9c28e0a25e5237c84a024e9e0dfeb402667f9c425a/diff',
    '/var/lib/docker/overlay2/cb5d89b07336336f7258660da1017bdbceae30192061e893a553a35497bb2afc/diff',
]

# 打开文件准备写入输出
with open('zookeeper_output.txt', 'w') as output_file:
    # 计算并打印每个文件夹的哈希值
    for directory in directories:
        folder_hash = hash_directory(directory, output_file)
        # output_file.write(f'The hash of the directory {directory} is: {folder_hash}\n')
