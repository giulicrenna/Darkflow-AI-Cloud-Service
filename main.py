from src.predictor import Predictor
from src.config import get_config

config: dict = get_config()

if __name__ == '__main__':
    try:
        my_model = Predictor(model_name=config['model_name'],
                                mqtt_address=config['mqtt_host'],
                                use_mqtt=False,
                                save_with_bbox=True,
                                show=True)
        pred = my_model.single_prediction()
        
        print(pred)
        
    except Exception as e:
        if e == KeyboardInterrupt:
            ...
        pass
    
    