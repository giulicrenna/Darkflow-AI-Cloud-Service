from ultralytics import YOLO
from config import get_config

import shutil
import os

config: dict = get_config()

DIR_PATH : str = os.path.join(os.getcwd(), 'datasets')
MODEL_PATH : str = os.path.join(os.getcwd(), 'model')
 
def train_model(yaml_path: str,
                training_name : str,
                model_name : str = 'yolov8m.pt',
                imgsz : int = 640,
                epochs : int = 10,
                batchsz : int = 8) -> None: 
    
    model_path : str = os.path.join(MODEL_PATH, model_name)
    
    try:
        model = YOLO(model_path)
    except FileNotFoundError:
        print('Model was not found on that directory.')
        os.chdir(MODEL_PATH)
        model = YOLO(model_name)
        print('RE-run this script.')
        
    # yaml_path debe ser la ruta a partir de ./datasets/{df_name}/{data.yaml}
    YAML_PATH : str = os.path.join(DIR_PATH, yaml_path)
    
    results = model.train(
       data=YAML_PATH,
       imgsz=640,
       epochs=10,
       batch=8,
       name=training_name
    )
    
if __name__ == '__main__':
    yaml : str = 'hojas/data.yaml'
    train_name : str = config['training_name']
    size: int = config['image_size']
    epochs: int = config['epochs']
    model: str = config['training_scheme']    
    
    train_model(yaml,
                train_name,
                model,
                size,
                epochs)