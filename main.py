import os
import sys
import base64
import requests
import uuid
import threading

from src.predictor import Predictor
from src.config import get_config
from src.barbecho import calculate_barbecho_percent
from src.logger import log
from src.utils import *

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

class IImage(BaseModel):
    imageId: str
    url: str
class Model(BaseModel):
    name: str
    version: str

class MultipleDetection(BaseModel):
    reportId: str
    model: Model
    environment: str
    images: list[IImage]

log(f'Initializing {os.path.basename(__file__)}.')

def download_image(url: str) -> str:
    try:
        image_name: str = str(uuid.uuid4()) + '.jpg'
        image_path: str = os.path.join(DOWNLOAD_PATH, image_name)
        image_bytes: bytes = requests.get(url).content

        with open(image_path, 'wb') as handler:
            handler.write(image_bytes)

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
            return pred

    except Exception as e:
        msg: str = f'Exception at {classification.__name__}() instance: {e}' 
        log(msg)

def task(data: MultipleDetection) -> None:
    MODEL: str = os.path.join(MODELS_PATH, f'{data.model.name}.pt')
    
    log(f'At task() instance: Loading {MODEL}')
    
    my_model = Predictor(model_name=MODEL,
                        use_mqtt=False,
                        show=False,
                        save_both=False,
                        save_predictions=False)
    
    for image in data.images:    
        # This dictionary will be sent to the darkflow server
        message: dict = {}
        message['reportId'] = data.reportId
        message['imageId'] = image.imageId
        
        image_path: str = download_image(image.url)
        
        if image_path != None:
            try:
                result: dict = classification(my_model, image_path)
                
                old_detections: list = [x for x in result['metadata']]
                IDetection: list = []
                
                for i in old_detections:
                    if i != 'None': 
                        box: dict = xyxy_to_darkflow(i['bbox']['x1'],
                                                    i['bbox']['y1'],
                                                    i['bbox']['x2'],
                                                    i['bbox']['y2'],
                                                    i['bbox']['height'],
                                                    i['bbox']['width'])
                        
                        detection: dict = {
                            'weedIdAI': i['object_name'],
                            'box' : box
                        }
                        IDetection.append(detection)

                message['detections'] = IDetection
                
                print(f'DEBUG: {message}')
                
                if data.environment == 'PROD':
                    response: str = requests.post(config['PROD_SERVER'], json = message).text
                    log(response)
                elif data.environment == 'DEV':
                    response: str = requests.post(config['DEV_SERVER'], json = message).text
                    log(response)
                
                os.remove(image_path)
                log(f'{os.path.basename(image_path)} : {message}')
            except Exception as e:
                type_, val, traceback = sys.exc_info()
                log(f'Exception at task(): while trying to procces image: \nType: {type_}\nValue: {val}\nTraceback: {traceback}')
    
    response: str = requests.post(config['END_DEV_SERVER'], json = {"reportId": data.reportId}).text
    log(response)
         
run : object = FastAPI()
"""
run.add_middleware(HTTPSRedirectMiddleware)
run.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)
"""

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
async def multiple_detection(item : MultipleDetection):     
    try:       
        MODEL: str = os.path.join(MODELS_PATH, f'{item.model.name}.pt')
        
        if not os.path.isfile(MODEL):
            return {'status' : 'ERROR',
                        'error': {
                            'message' : 'Model does not exist'
                        }
                    }
        
        t = threading.Thread(target=task, 
                         args =(item,))
        t.start()
        
        return {'status' : 'OK',
                        'error': {
                            'message' : None
                        }
                    }
    except Exception as error:
        log(f'exception at simple_detection() instance: {error}')
        return {'status' : 'ERROR',
                        'error': {
                            'message' : error
                        }
                    }
    
    return {'status' : 'OK',
                        'error': {
                            'message' : 'Task Initialized Succesfully'
                        }
                    }

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


@run.get("/download_new_model")
async def download_new_model(model_name: str, model_url: str):     
    MODEL_PATH = os.path.join(os.getcwd(), 'model', f'{model_name}.pt')
    try:         
        response = requests.get(model_url)
        if response.status_code == 200:
            with open(MODEL_PATH, 'wb') as f:
                f.write(response.content)
                
        return 200
                        
    except Exception as error:
        log(f'exception at simple_detection() instance: {error}')
        return {'exception': f'{error}'}

"""
uvicorn main:run --host localhost --port 80
"""
  
if __name__ == "__main__":
    config = uvicorn.Config("main:run",
                            host=config['api_host'],
                            port=config['api_port'],
                            log_level="info")
    server = uvicorn.Server(config)
    server.run()
    
