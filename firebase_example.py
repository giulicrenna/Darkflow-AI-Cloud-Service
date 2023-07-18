from src.predictor import Predictor
from src.config import get_config
from src.firebase import FirestoreConnector
import os
import base64

config: dict = get_config()

if __name__ == '__main__':
    try:
        firebase_conn = FirestoreConnector(train_path='drone/')
        files: list  = firebase_conn.update_files_list('drone/')
        
        my_model = Predictor(model_name=config['model_name'],
                                mqtt_address=config['mqtt_host'],
                                use_mqtt=False,
                                show=True,
                                save_both=False,
                                save_predictions=True)
        
        
        print('AVAILABLE FILES: ')
        for file in files:
            print(f'\t- {file}')
        
        firebase_conn.download_images_stack()

        for file in os.listdir('downloads/'):
            with open(os.path.join('downloads', file), 'rb') as image:
                encoded_str: str = base64.b64encode(image.read())    
                pred : str = my_model.predict_from_b64(encoded_str)

                print(pred)
        
        print('Uploading Files')
        firebase_conn.upload_image_stack()

    except Exception as e:
        if e == KeyboardInterrupt:
            ...
        print(f'Exception: {e}')
    
    