from fastapi import FastAPI, UploadFile, BackgroundTasks
import uvicorn
import minio_service

app = FastAPI()


@app.post("/minio/upload", summary="上传文件到minio")
async def upload(file: UploadFile):
    return await minio_service.upload(file)

# @app.post("/minio/upload_", summary="上传文件到minio")
# async def upload(file: UploadFile):
#     return await minio_service.upload_(file)

@app.post("/minio/download", summary="从minio下载")
async def download(model_name: str, background_task: BackgroundTasks):
    return await minio_service.download(model_name, background_task)

# @app.post("/minio/download_", summary="从minio下载")
# async def download(model_name: str, background_task: BackgroundTasks):
#     return await minio_service.download_(model_name, background_task)

@app.post("/minio/delete_all", summary=" 删除所有信息")
async def delete_all():
    return await minio_service.delete_all()

# @app.post("/minio/delete_all_", summary=" 删除所有信息")
# async def delete_all():
#     return await minio_service.delete_all_2()

# TODO: 未实现 
# @app.post("/minio/delete", summary="根据 model_name 删除信息")
# async def delete_by_model_name(model_name: str):
#    return await minio_service.delete_by_model_name(model_name)

if __name__ == "__main__":
    uvicorn.run(app='main:app', host='0.0.0.0', port=8000, reload=True)