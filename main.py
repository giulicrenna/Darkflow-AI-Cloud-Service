from src.predictor import Predictor
from src.config import get_config
from src.firebase import FirestoreConnector, FirestoreRealTimeDatabase
from src.logger import log
import os
import base64

config: dict = get_config()
    
log(f'Initializing {os.path.basename(__file__)}.')

firebase_database = FirestoreRealTimeDatabase()

firebase_conn = FirestoreConnector(train_path='drone/')

my_model = Predictor(model_name=config['model_name'],
                        mqtt_address=config['mqtt_host'],
                        use_mqtt=False,
                        show=True,
                        save_both=False,
                        save_predictions=True)

def runner() -> None:
    try:        
        """
        print('AVAILABLE FILES: ')
        for file in files:
            print(f'\t- {file}')
        """
        
        while True:
            files: list  = firebase_conn.update_files_list('drone/')
            
            log(f'Attempt to download images.')
            are_new_files: bool = firebase_conn.download_images_stack()

            if are_new_files:
                for file in os.listdir('downloads/'):
                    with open(os.path.join('downloads', file), 'rb') as image:
                        filename_without_extension: str = file.split('.')[0]
                        
                        if not firebase_database.register_exists(filename_without_extension):  
                            encoded_str: str = base64.b64encode(image.read())    
                            pred : str = my_model.predict_from_b64(encoded_str, filename_without_extension)

                            firebase_database.appendData(pred, filename_without_extension)
                            logging: str = f'{file} : {pred}' 
                            print(logging)
                            log(logging)
                
            
            print('Uploading Files')
            firebase_conn.upload_image_stack()

    except Exception as e:
        if e == KeyboardInterrupt:
            os._exit()
        msg: str = f'Exception: {e}' 
        log(msg)
        print(msg)
        

if __name__ == '__main__':
    while True:
        try:
            runner()
        except:
            pass
    
    
    