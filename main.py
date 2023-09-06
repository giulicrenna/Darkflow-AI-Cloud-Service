import os
import base64
import requests
import uuid
import threading

from src.predictor import Predictor
from src.config import get_config
from src.barbecho import calculate_barbecho_percent
from src.logger import log

from PIL import Image
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
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
        image_bytes: bytes = requests.get(url, stream = True).raw
        img = Image.open(image_bytes)
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
        msg: str = f'Exception at {classification.__name__}() instance: {e}' 
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

run.add_middleware(HTTPSRedirectMiddleware)
run.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

@run.get("/")
async def root() -> None:
    return {'status' : 'ok'}

@run.get("/barbecho")
async def barbecho(url: str) -> dict:
    try:
        IMG_PATH: str = download_image(url)
        data: dict = calculate_barbecho_percent(IMG_PATH)
        os.remove(IMG_PATH)
        return data
    except Exception as e:
        return {'Exception' : e}
        
@run.post("/multiple_detection")
async def multiple_detection(item : TaskPetition):     
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

@run.get("/single_detection")
async def single_detection(model: str, url: str):     
    try:       
        MODEL: str = os.path.join(MODELS_PATH, model)
        
        if not os.path.isfile(MODEL):
            return {'Status' : 'Model does not exists'}
        
        my_model = Predictor(model_name=model,
                        use_mqtt=False,
                        show=False,
                        save_both=False,
                        save_predictions=False)
  
        image_path: str = download_image(url)
        
        if image_path != None:
            result: dict = classification(my_model, image_path)
            os.remove(image_path)
            log(f'{os.path.basename(image_path)} : {result}')
            return result
        
        return {'Status':'Could not make any inference'}
                        
    except Exception as error:
        log(f'exception at simple_detection() instance: {error}')
        return {'exception': f'{error}'}

@run.get("/available_models")
async def available_models():     
    try:       
        models_in_dir: list = os.listdir(MODELS_PATH)
        return {'available_models' : models_in_dir}
                        
    except Exception as error:
        log(f'exception at simple_detection() instance: {error}')
        return {'exception': f'{error}'}
    
"""
if __name__ == "__main__":
    config = uvicorn.Config("main:run",
                            host=config['api_host'],
                            port=config['api_port'],
                            log_level="info")
    server = uvicorn.Server(config)
    server.run()
"""
    
