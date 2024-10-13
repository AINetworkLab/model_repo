from entity import SessionLocal, ModelInfo, ModelInfo_2, LocationInfo
from sqlalchemy import text, update

session = SessionLocal()

def get_model_by_layer_hash_all(layer_hash: str):
    try:
        return session.query(ModelInfo).filter(ModelInfo.layer_hash == layer_hash).all()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def get_model_by_layer_hash(layer_hash: str):
    try:
        return session.query(ModelInfo_2).filter(ModelInfo_2.layer_hash == layer_hash).all()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def add_model(model: ModelInfo):
    try:
        session.add(model)
        session.commit()
        session.refresh(model)
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def add_model_2(model: ModelInfo_2):
    try:
        session.add(model)
        session.commit()
        session.refresh(model)
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def add_location(location: LocationInfo):
    try:
        session.add(location)
        session.commit()
        session.refresh(location)
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def existing_models(model: ModelInfo):
    try:
        models = session.query(ModelInfo).filter(
            ModelInfo.layer_hash == model.layer_hash,
            ModelInfo.model_name == model.model_name,
            ModelInfo.minio_id == model.minio_id,
            ModelInfo.layer_number == model.layer_number,
            ModelInfo.layer_name == model.layer_name).all()
        return models
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def existing_models_2(model: ModelInfo_2):
    try:
        # 利用联合索引进行过滤
        query = session.query(ModelInfo_2).filter(
            ModelInfo_2.layer_hash == model.layer_hash,
            ModelInfo_2.model_name == model.model_name
        )
        query = query.filter(
            ModelInfo_2.layer_num == model.layer_num,
            ModelInfo_2.layer_name == model.layer_name
        )
        models = query.all()
        return models
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def get_model_by_model_name(model_name: str):
    try:
        return session.query(ModelInfo).filter(ModelInfo.model_name == model_name).all()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def get_model_by_model_name_2(model_name: str):
    try:
        return session.query(ModelInfo_2).filter(ModelInfo_2.model_name == model_name).all()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def get_minio_id(layer_hash: str):
    try:
        return session.query(LocationInfo).filter(LocationInfo.layer_hash == layer_hash).first()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

    return

def delete_all():
    try:
        truncate_sql = text("TRUNCATE TABLE models;")
        session.execute(truncate_sql)
        session.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

def delete_all_2():
    try:
        truncate_sql = text("TRUNCATE TABLE model;")
        session.execute(truncate_sql)
        session.commit()
        truncate_sql = text("TRUNCATE TABLE location;")
        session.execute(truncate_sql)
        session.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()
# def delete_by_model_name(model_name: str):
#     try:
#         delete_sql = text("DELETE FROM models WHERE model_name = :model_name")
#         session.execute(delete_sql, {"model_name": model_name})
#         session.commit()
#     except Exception as e:
#         return {"error": str(e)}
#     finally:
#         session.close()

# 没有关闭session

# def get_model_by_layer_hash_all(layer_hash: str):
#     return session.query(ModelInfo).filter(ModelInfo.layer_hash == layer_hash).all()


# def add_model(model: ModelInfo):
#     session.add(model)
#     session.commit()
#     session.refresh(model)

# def existing_models(model: ModelInfo):
#     models = session.query(ModelInfo).filter(
#         ModelInfo.layer_hash == model.layer_hash,
#         ModelInfo.model_name == model.model_name,
#         ModelInfo.minio_id == model.minio_id,
#         ModelInfo.layer_number == model.layer_number,
#         ModelInfo.layer_name == model.layer_name).all()
#     return models

# def get_model_by_model_name(model_name: str):
#     return session.query(ModelInfo).filter(ModelInfo.model_name == model_name).all()


# def delete_all():
#     truncate_sql = text("TRUNCATE TABLE models;")
#     session.execute(truncate_sql)
#     session.commit()