import requests
import torch
import os
from transformers import AutoImageProcessor, ResNetForImageClassification
from datasets import load_dataset

def main(args):
    url = "http://172.17.0.1:8000/minio/download"
    params = {
        "model_name": "resnet-50"
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        try:
            file_stream = response.content
            os.makedirs("/tmp/resnet", exist_ok=True)
            path = "/tmp/resnet/pytorch_model.bin"
            with open(path, "wb") as f:
                f.write(file_stream)
            # file_size = os.path.getsize(path)
            # file_size_mb = file_size / (1024 * 1024)
            # print("File size:", file_size_mb, "MB")
            # 配置文件的URL
            config_url = "https://huggingface.co/microsoft/resnet-50/resolve/main/config.json"
            # 下载并保存配置文件
            res = requests.get(config_url)
            res.raise_for_status()  # 确保请求成功
            with open("/tmp/resnet/config.json", "wb") as f:
                f.write(res.content)
            try:
                dataset = load_dataset("huggingface/cats-image")
                image = dataset["test"]["image"][0]
                processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
                model = ResNetForImageClassification.from_pretrained("/tmp/resnet/")
                inputs = processor(image, return_tensors="pt")
                with torch.no_grad():
                    logits = model(**inputs).logits

                # model predicts one of the 1000 ImageNet classes
                predicted_label = logits.argmax(-1).item()
                # print(model.config.id2label[predicted_label])
                return {"Predicted class:": model.config.id2label[predicted_label]}
            except FileNotFoundError:
                return {"error": "Model file not found"}
            except RuntimeError as e:
                return {"error": str(e)}
        except Exception as e:
            return {"erro":str(e)}