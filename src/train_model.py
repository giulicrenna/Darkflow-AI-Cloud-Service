from ultralytics import YOLO
import os

DIR_PATH : str = os.path.join(os.getcwd(), 'datasets')
 
 
def train_model(yaml_path: str, training_name : str, model : str = 'yolov8m.pt') -> None: 
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
    yaml : str = 'pothole/pothole.yaml'
    train_name : str = 'baches'
    
    train_model(yaml, train_name)