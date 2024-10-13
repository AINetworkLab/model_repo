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
    '/var/lib/docker/overlay2/74c26cf43b04f88c16b6e7211f04d43cfd0c5bb31e7e9fa7e4f7c515fe48dd2f/diff',
    '/var/lib/docker/overlay2/e1e0ebcf6a88f560b2cd7480bff140943aee8e94f8135e723489e5be4ce19cc7/diff',
    '/var/lib/docker/overlay2/4e892e04c9605d0209c4292cc67e1d4986be1ac34b7bc30dd2e0cebd083d4280/diff',
    '/var/lib/docker/overlay2/5c1a62f47360dd02a0cf9451b0cc184639aed203e520fb24800f6f81010661ca/diff',
    '/var/lib/docker/overlay2/17b05b2eb301002332727a9395642f5a85d6338b8b1bd4e89d3ba0c0757758a0/diff',
]

# 打开文件准备写入输出
with open('ubuntu_zookeeper_output.txt', 'w') as output_file:
    # 计算并打印每个文件夹的哈希值
    for directory in directories:
        folder_hash = hash_directory(directory, output_file)
        # output_file.write(f'The hash of the directory {directory} is: {folder_hash}\n')
