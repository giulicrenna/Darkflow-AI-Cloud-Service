from src.predictor import Predictor
from src.config import get_config

config: dict = get_config()

if __name__ == '__main__':
    while True:
        try:
            my_model = Predictor(model_name=config['model_name'],
                                 mqtt_address=config['mqtt_host'],
                                 use_mqtt=True, show=True)
            pred = my_model.keep_prediction()
            
            print(pred)
            
        except Exception as e:
            if e == KeyboardInterrupt:
                break
            pass
        
    