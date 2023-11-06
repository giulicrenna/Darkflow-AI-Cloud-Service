from ultralytics import YOLO
from config import get_config

import argparse
import yaml
import math
import datetime
import requests
import os

# PREPARE ALL CONFIGS
parser = argparse.ArgumentParser(description='YOLO Trainer from Darkflow API')
parser.add_argument('-u', '--url', type=str, help='Url to the dataset')
args = parser.parse_args()
data_source: dict = {
    "url" : args.url
}

config: dict = get_config()

# PREPARE USEFUL PATHS
DIR_PATH : str = os.path.join(os.getcwd(), 'datasets')
MODEL_PATH : str = os.path.join(os.getcwd(), 'model')
DATASET_PATH : str = os.path.join(os.getcwd(), 'dataset')


def darkflow_to_yolo(top: int, left: int, width: int,height: int) -> dict:
    top /= 100
    left /= 100
    width /= 100
    height /= 100
    
    return {
        "y" : top + height/2,
        "x" : left + width/2,
        "w" : width,
        "h" : height
    }

def download_image(url: str, path: str) -> None:
    img_data = requests.get(url).content
    with open(path, 'wb') as handler:
        handler.write(img_data)

"""
FOLDER CREATION:

CURRENT_DATASET_PATH
|
|- TRAINING_PATH
|               |- TRAINING_IMAGES_PATH
|               |- TRAINING_LABELS_PATH
|
|- VALIDATION_PATH
|                 |- VALIDATION_IMAGES_PATH
|                 |- VALIDATION_LABELS_PATH

"""
def create_dataset(source: dict = data_source) -> str:
    current_time = str(datetime.datetime.now())[0:18].replace(" ", "_").replace(":", "_")
    
    CURRENT_DATASET_PATH: str = os.path.join(DATASET_PATH, current_time)
    
    TRAINING_PATH: str = os.path.join(CURRENT_DATASET_PATH, "training")
    TRAINING_IMAGES_PATH: str = os.path.join(TRAINING_PATH, "images")
    TRAINING_LABELS_PATH: str = os.path.join(TRAINING_PATH, "labels")
    
    VALIDATION_PATH: str = os.path.join(CURRENT_DATASET_PATH, "val")
    VALIDATION_IMAGES_PATH: str = os.path.join(VALIDATION_PATH, "images")
    VALIDATION_LABELS_PATH: str = os.path.join(VALIDATION_PATH, "labels")
    
    
    if not os.path.isdir(CURRENT_DATASET_PATH): os.makedirs(CURRENT_DATASET_PATH)
    
    if not os.path.isdir(TRAINING_IMAGES_PATH): os.makedirs(TRAINING_IMAGES_PATH)
    if not os.path.isdir(TRAINING_LABELS_PATH): os.makedirs(TRAINING_LABELS_PATH) 
       
    if not os.path.isdir(VALIDATION_IMAGES_PATH): os.makedirs(VALIDATION_IMAGES_PATH)
    if not os.path.isdir(VALIDATION_LABELS_PATH): os.makedirs(VALIDATION_LABELS_PATH)
    
    # GET DATA FROM THE API
    metadata: requests.Response = requests.get(source["url"])
    if metadata.status_code != 200:
        raise requests.ConnectionError
    
    metadata = dict(metadata.json())
    images_data: list = metadata['dataSet']
    dataset_classes: list = []
    
    # SPLIT THE VALIDATION AND TRAINING SET
    images_len: int = len(images_data)
    train_len: int = math.ceil(images_len//3 * 2) if images_len != 1 else 1
    print(f'Traing len: {train_len}')
    count: int = 0
    
    for data in images_data: # EACH IMAGE
        DIRECTORY_IMAGE: str = TRAINING_IMAGES_PATH if count <= train_len else VALIDATION_IMAGES_PATH
        DIRECTORY_LABEL: str = TRAINING_LABELS_PATH if count <= train_len else VALIDATION_LABELS_PATH
        count += 1
        
        image_name: str = data["id"]
        image_url: str = data["image"]
        images_detetions: list = data["detections"]
        
        IMAGE_FINAL_PATH: str = os.path.join(DIRECTORY_IMAGE, f'{image_name}.jpeg')
        TXT_FINAL_PATH: str = os.path.join(DIRECTORY_LABEL, f'{image_name}.txt')
        
        if not os.path.isfile(TXT_FINAL_PATH): open(TXT_FINAL_PATH, 'x+')
        
        download_image(image_url, IMAGE_FINAL_PATH)
        
        for detection in images_detetions: # EACH  DETECTION
            # DETERMINE THE FIGURE CLASS
            CURRENT_CLASS: str = detection["weed"]["name"]
            dataset_classes.append(CURRENT_CLASS)
            dataset_classes = list(set(dataset_classes))
            CLASS: int = dataset_classes.index(CURRENT_CLASS)
            # DETERMINE THE BOX VALUES AND CONSTRUCT TXT
            BOX: dict = detection["box"]
            
            TOP: float = int(BOX["top"])
            LEFT: float = int(BOX["left"])
            
            WIDTH: float = int(BOX["width"])
            HEIGHT: float = int(BOX["height"])
            
            box_: dict = darkflow_to_yolo(TOP, LEFT, WIDTH, HEIGHT)
            box_x = round(box_["x"], 3)
            box_y = round(box_["y"], 3)
            box_w = round(box_["w"], 3)
            box_h = round(box_["h"], 3)
            
            TEXT: str = f"{CLASS} {box_x} {box_y} {box_w} {box_h}\n"
            open(TXT_FINAL_PATH, "a").write(TEXT)
    
    # YAML CREATION
    YAML_PATH: str = os.path.join(CURRENT_DATASET_PATH, "data.yaml")
    
    yaml_data: dict = {
        "train" : "./training/images",
        "val" : "./val/images",
        "nc": len(dataset_classes),
        "names" : dataset_classes
    }

    with open(YAML_PATH, 'w') as file: yaml.dump(yaml_data, file, default_flow_style=False)

    return CURRENT_DATASET_PATH
    
def train_model(yaml_path: str,
                training_name : str,
                model_name : str = 'yolov8x.pt',
                imgsz : int = 640,
                epochs : int = 10,
                batchsz : int = 8,
                device = None) -> None: 
    
    model_path : str = os.path.join(MODEL_PATH, model_name)
    
    try:
        model = YOLO(model_path)
    except FileNotFoundError:
        print('Model was not found on that directory.')
        os.chdir(MODEL_PATH)
        model = YOLO(model_name)
        print('RE-run this script.')
        
    # yaml_path debe ser la ruta a partir de ./datasets/{df_name}/{data.yaml}
    # YAML_PATH : str = os.path.join(DIR_PATH, yaml_path)
    
    results = model.train(
       data=yaml_path,
       imgsz=imgsz,
       epochs=epochs,
       batch=batchsz,
       name=training_name,
       device=device
    )
    return results

if __name__ == '__main__':
    DS_PATH: str = create_dataset()
    
    yaml_ : str = os.path.join(DS_PATH, 'data.yaml')
    
    train_name : str = config['training_name']
    size: int = config['image_size']
    epochs: int = config['epochs']
    model: str = config['training_scheme']    
    batch: int = config['batch']
    device: object = config["device"] 

    train_model(yaml_,
                training_name=train_name,
                model_name=model,
                imgsz=size,
                epochs=epochs,
                batchsz=batch,
                device=device)
    