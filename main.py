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

def clean_folder(folder_name: str = 'downloads') -> None:
    DOWNLOADS_PATH: str = os.path.join(os.getcwd(), folder_name)
    
    for file in os.listdir(DOWNLOADS_PATH):
        file_path: str = os.path.join(DOWNLOADS_PATH, file)
        
        if os.path.isfile(file_path):
            os.remove(file_path)

def task(model: str,
         source_path: str,
         upload_path: str = 'detections/',
         upload_detections: bool = False) -> None:
    my_model = Predictor(model_name=model,
                        mqtt_address=config['mqtt_host'],
                        use_mqtt=False,
                        show=False,
                        save_both=False,
                        save_predictions=True)
    
    try:                
        while True:
            files: list  = firebase_conn.update_files_list(source_path)
            
            are_new_files: bool = firebase_conn.download_images_stack()

            if are_new_files:
                for file in os.listdir('downloads/'):
                    with open(os.path.join('downloads', file), 'rb') as image:
                        filename_without_extension: str = file.split('.')[0]
                        
                        if not firebase_database.register_exists(filename_without_extension):  
                            """
                            Make the classification from the base64 images
                            """
                            encoded_str: str = base64.b64encode(image.read())    
                            pred : str = my_model.predict_from_b64(encoded_str, filename_without_extension, {'source_path' :source_path})

                            """
                            Upload the JSON with the name of the file
                            """
                            firebase_database.appendData(pred, filename_without_extension)
                            logging: str = f'{file} : {pred}' 
                            print(logging)
                            log(logging)
            
            if upload_detections:
                log('Uploading Files')
                firebase_conn.upload_image_stack(source_path=upload_path)
                
            clean_folder()

    except Exception as e:
        if e == KeyboardInterrupt:
            os._exit()
        msg: str = f'Exception: {e}' 
        log(msg)
        print(msg)
        

if __name__ == '__main__':
    task(model='darkflow-test.pt',
         source_path='drone')
    
    
    