from src.predictor import Predictor
from src.b64_encoder import export_b64
from src.config import get_config
from src.logger import log
from src.compressor import *

from fastapi import FastAPI
import uvicorn

#  uvicorn api:run --reload

config : dict = get_config()

my_model = Predictor(model_name=config['model_name'],
                                mqtt_address=config['mqtt_host'],
                                use_mqtt=False,
                                show=True)

run : object = FastAPI()

@run.get("/")
async def root() -> None:
     return {'status' : 'ok'}
     
@run.get("/simple_detection")
async def simple_detection(img_data : str):     
    pred : str = ''
    try:   
        img_data = decompress(img_data)
        
        pred = my_model.predict_from_b64(img_data)    
        
    except Exception as error:
        return {'exception': f'{error}'}
    
    return pred

if __name__ == "__main__":
    config = uvicorn.Config("api:run",
                            host=config['api_host'],
                            port=config['api_port'],
                            log_level="info")
    server = uvicorn.Server(config)
    server.run()

