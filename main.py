from src.predictor import Predictor
from src.b64_encoder import export_b64
from src.config import get_config

config: dict = get_config()

if __name__ == '__main__':
    try:
        my_model = Predictor(model_name=config['model_name'],
                                mqtt_address=config['mqtt_host'],
                                use_mqtt=False,
                                show=True)
        
        data_b64 : str = export_b64() 
        print(data_b64)
        pred : str = my_model.predict_from_b64(data_b64)
        
        print(pred)
        
    except Exception as e:
        if e == KeyboardInterrupt:
            ...
        print(f'Exception: {e}')
    
    