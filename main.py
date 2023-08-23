import os
import base64
import requests
import uuid
import threading

from src.predictor import Predictor
from src.config import get_config
from src.logger import log

from PIL import Image
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


DOWNLOAD_PATH: str = os.path.join(os.getcwd(), 'downloads')
MODELS_PATH: str = os.path.join(os.getcwd(), 'model')
config: dict = get_config()

log(f'Initializing {os.path.basename(__file__)}.')

def download_image(url: str) -> str:
    try:
        image_name: str = str(uuid.uuid4()) + '.jpg'
        image_path: str = os.path.join(DOWNLOAD_PATH, image_name)
        img = Image.open(requests.get(url, stream = True).raw)
        img.save(image_path)

        return image_path
    except Exception as e:
        log(f'In download_image() instance: {e}')
        return None
        
def clean_folder(folder_name: str = 'downloads') -> None:
    DOWNLOADS_PATH: str = os.path.join(os.getcwd(), folder_name)
    
    for file in os.listdir(DOWNLOADS_PATH):
        file_path: str = os.path.join(DOWNLOADS_PATH, file)
        
        if os.path.isfile(file_path):
            os.remove(file_path)

def classification(model: Predictor,
         image_path: str,
         upload_detections: bool = False) -> dict:
    
    try:                
        with open(image_path, 'rb') as image:
            """
            Make the classification from the base64 images
            """
            encoded_str: str = base64.b64encode(image.read())    
            pred : dict = model.predict_from_b64(encoded_str)

            """
            Upload the JSON with the name of the file
            """
            logging: str = f'{image_path} : {pred}' 
            #log(logging)
            
            return pred

    except Exception as e:
        msg: str = f'Exception at task() instance: {e}' 
        log(msg)

def task(model: str, img_arr: list) -> None:
    my_model = Predictor(model_name=model,
                        use_mqtt=False,
                        show=False,
                        save_both=False,
                        save_predictions=False)
    
    for image in img_arr:    
        image_path: str = download_image(image)
        if image_path != None:
            result: dict = classification(my_model, image_path)
            os.remove(image_path)
            log(f'{os.path.basename(image_path)} : {result}')
            #print(result)

class TaskPetition(BaseModel):
    model: str
    img_arr: List[str]

run : object = FastAPI()

@run.get("/")
async def root() -> None:
     return {'status' : 'ok'}
     
@run.post("/simple_detection")
async def simple_detection(item : TaskPetition):     
    try:       
        MODEL: str = os.path.join(MODELS_PATH, item.model)
        
        t = threading.Thread(target=task, 
                         args =(item.model, item.img_arr,))
        
        t.start()
        
        if not os.path.isfile(MODEL):
            return {'Status' : 'Model does not exists'}
                
    except Exception as error:
        log(f'exception at simple_detection() instance: {error}')
        return {'exception': f'{error}'}
    
    return {'Status' : 'Task Initialized Succesfully'}

"""
if __name__ == "__main__":
    config = uvicorn.Config("main:run",
                            host=config['api_host'],
                            port=config['api_port'],
                            log_level="info")
    server = uvicorn.Server(config)
    server.run()
"""
    
