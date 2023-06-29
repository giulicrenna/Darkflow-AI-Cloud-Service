from ultralytics import YOLO
from config import get_config
import os

config: dict = get_config()
DIR_PATH : str = os.path.join(os.getcwd(), 'datasets')
 
def train_model(yaml_path: str,
                training_name : str,
                model : str = 'yolov8m.pt',
                imgsz : int = 640,
                epochs : int = 10,
                batchsz : int = 8) -> None: 
    model = YOLO(model)
    
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