from entity import SessionLocal, DataInfo
from sqlalchemy import text, update

session = SessionLocal()

def add_data(data: DataInfo):
    try:
        session.add(data)
        session.commit()
        session.refresh(data)
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def delete_all():
    try:
        sql = text("TRUNCATE TABLE storage_data;")
        session.execute(sql)
        session.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

# def delete_by_model_name(model_name: str):
#     try:
#         sql = text("DELETE FROM storage_data WHERE model_name = :model_name")
#         session.execute(sql, {"model_name": model_name})
#         session.commit()
#     except Exception as e:
#         return {"error": str(e)}
#     finally:
#         session.close()


# 没有关闭session
# def add_data(data: DataInfo):
#     session.add(data)
#     session.commit()
#     session.refresh(data)

# def delete_all():
#     sql = text("TRUNCATE TABLE storage_data;")
#     session.execute(sql)
#     session.commit()