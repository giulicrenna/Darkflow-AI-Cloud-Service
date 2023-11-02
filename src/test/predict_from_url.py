from ultralytics import YOLO
import os
import argparse

os.system('cls')
MODEL_PATH: str = os.path.join(os.getcwd(), 'model')

parser = argparse.ArgumentParser(description='YOLO Trainer from Darkflow API')
parser.add_argument('-u', '--url', type=str, help='Url to the dataset')
parser.add_argument('-m', '--model', type=str, help='Url to the dataset')

args = parser.parse_args()

url: str = args.url
model_name: str = args.model
conf: int = 0.25  

available_models: list = os.listdir(MODEL_PATH)

if __name__ == '__main__':
    if model_name not in available_models:
        print('Modelo Inexistente')
    else:
        model = YOLO(os.path.join(MODEL_PATH, model_name))
        results = model.predict(source=url,
                                show=False,
                                save=True,
                                conf=conf,
                                )
        print(results)
    
    
"""
https://www.jardineros.mx/site/qanda/135623/1924/1924_croped.jpg
"""