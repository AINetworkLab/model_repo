from entity import SessionLocal, StorageInfo
from sqlalchemy import text, update
session = SessionLocal()

def get_storage_all():
    try:
        return session.query(StorageInfo).all()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def get_storage_by_minio_id(minio_id:str):
    try:
        return session.query(StorageInfo).filter(StorageInfo.minio_id == minio_id).first()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def update_used_storage(file_size:int,storage:StorageInfo,minio_id:str):
    try:
        current_free_space = int(storage.free_space)
        new_free_space = current_free_space - file_size
        new_used_space = int(storage.used_space) + file_size
        stmt = (
            update(StorageInfo)
            .where(StorageInfo.minio_id == minio_id)
            .values(
                free_space=str(new_free_space),
                used_space=str(new_used_space)
            )
        )
        session.execute(stmt)
        session.commit()
        session.refresh(storage)
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def refresh_storage():
    try:
        s_sql = text("UPDATE storage SET used_space = '0', free_space = total_space;")
        session.execute(s_sql)
        session.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()


# 没有关闭session
# def get_storage_all():
#     return session.query(StorageInfo).all()

# def get_storage_by_minio_id(minio_id:str):
#     return session.query(StorageInfo).filter(StorageInfo.minio_id == minio_id).first()

# def update_used_storage(file_size:int,storage:StorageInfo,minio_id:str):
#     current_free_space = int(storage.free_space)
#     new_free_space = current_free_space - file_size
#     new_used_space = int(storage.used_space) + file_size
#     stmt = (
#         update(StorageInfo)
#         .where(StorageInfo.minio_id == minio_id)
#         .values(
#             free_space=str(new_free_space),
#             used_space=str(new_used_space)
#         )
#     )
#     session.execute(stmt)
#     session.commit()
#     session.refresh(storage)

# def refresh_storage():
#     s_sql = text("UPDATE storage SET used_space = '0', free_space = total_space;")
#     session.execute(s_sql)
#     session.commit()