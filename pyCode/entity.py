from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, text, update ,Double

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
    layer_location = Column(String(255), nullable=False)
    layer_size = Column(Double, nullable=False)

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
    complete = Column(Integer, nullable=False)  # 是否全部上传完成

class ModelInfo_2(Base):
    __tablename__ = 'model'

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255), nullable=False)
    layer_num = Column(Integer, nullable=False)
    layer_hash = Column(String(255), nullable=False)
    layer_name = Column(String(255), nullable=False)

class LocationInfo(Base):
    __tablename__ = 'location'

    layer_hash = Column(String(255), primary_key=True, nullable=False)
    layer_location = Column(String(255), nullable=False)
    minio_id = Column(String(255), nullable=False)