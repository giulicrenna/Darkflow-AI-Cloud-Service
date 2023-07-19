import os
import uuid
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage


KEY_PATH: str = os.path.join(
    os.getcwd(),
    'firebase_key.json'
)
DOWNLOAD_PATH: str = os.path.join(
    os.getcwd(),
    'downloads'
)
FINAL_DETECTIONS_PATH: str = os.path.join(
    os.getcwd(),
    'detections'
)
PATH_CLOUD_DETECTIONS: str = 'detections/'
PATH_CLOUD_TRAIN: str = 'PhotoCel/'

BUCKET: str = 'cda-darkflow.appspot.com'

DATABASE: str = 'https://cda-darkflow-default-rtdb.firebaseio.com/'

firebaseConfig : dict = {
  'apiKey': "AIzaSyDjPV6kw5YJoAcmU0fxAe7G_7oEr49ite4",
  'authDomain': "cda-darkflow.firebaseapp.com",
  'databaseURL': "https://cda-darkflow-default-rtdb.firebaseio.com",
  'projectId': "cda-darkflow",
  'storageBucket': "cda-darkflow.appspot.com",
  'messagingSenderId': "441003554485",
  'appId': "1:441003554485:web:4600d5c168b1c6411930fc",
  'measurementId': "G-982YYWSWEJ",
  "serviceAccount" : f"{KEY_PATH}",
  'database' : f'{DATABASE}'
}

class FirestoreConnector():
    def __init__(self,
                 firebase_config: dict = firebaseConfig,
                 bucket_name: str = BUCKET,
                 train_path: str = PATH_CLOUD_TRAIN,
                 detection_path: str = PATH_CLOUD_DETECTIONS,
                 download_path: str = DOWNLOAD_PATH) -> None:
            
        self.firebase_config = firebase_config
        self.train_path = train_path
        self.detection_path = detection_path
        self.download_path = download_path
        self.bucket_name = bucket_name
        
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': self.bucket_name
            })
        

        self.files_list: list = []
        
    def update_files_list(self,
                   path: str = PATH_CLOUD_TRAIN) -> list:
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix=path)

        temp_files: list = []
        
        for blob in blobs:
            if not str(blob.name).endswith('/'):
                temp_files.append(blob.name)
        
        self.files_list = temp_files
        
        return self.files_list
    
    def files_list(self,
                   path: str = PATH_CLOUD_TRAIN) -> list:
        
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix=path)

        temp_files: list = []
        
        for blob in blobs:
            if not str(blob.name).endswith('/'):
                temp_files.append(blob.name)
        
        return temp_files
    
    def download_images_stack(self) -> None:
        if len(self.files_list) <= 0:
            print('No files in memory.\n¿Have you runned FirestoreConnector.files_list()?')
            return
        if not os.path.isdir(self.download_path):
            os.mkdir(self.download_path)
        
        current_downloaded: list = os.listdir(self.download_path)
        
        bucket = storage.bucket()
        
        for file in self.files_list:
            filename: str = str(file).split('/')[1] + ".jpeg"

            if not filename in current_downloaded:
                blob = bucket.blob(file)
                print(f'Downloading: {filename} ')
                blob.download_to_filename(os.path.join(self.download_path, filename))

    def upload_image_stack(self,
                           final_detections_path: str = FINAL_DETECTIONS_PATH,
                           source_path: str = None) -> None:
        if source_path == None:
            source_path = self.detection_path
        
        for file in os.listdir(final_detections_path):
            cloud_path: str = os.path.join(source_path + file)
            local_path: str = os.path.join(final_detections_path, file)
            bucket = storage.bucket()
            blob = bucket.blob(cloud_path)
            blob.upload_from_filename(local_path)
            
                

