import os
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
from src.logger import log
from src.check_processed import check_processed

KEY_PATH: str = os.path.join(
    os.getcwd(),
    'json',
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

cred = credentials.Certificate(KEY_PATH)

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

class FirestoreRealTimeDatabase():
    def __init__(self,
                 databaseURL: str = 'https://cda-darkflow-detections-metadata.firebaseio.com/',
                 reference: str = 'detections') -> None:
        self.database: dict =  {'databaseURL': databaseURL}
        self.reference = reference
        self.app_name = 'RealtimeDatabaseConnector'
        
        self.RTD = firebase_admin.initialize_app(cred, self.database, self.app_name)
        log('Firestore realtime database initialized.')
        
    def appendData(self, dataJSON: dict, dataReference: str) -> None:
        try:
            reference = db.reference(f'{self.reference}/{dataReference}', self.RTD)
            reference.set(dataJSON)
        except Exception as e:
            log(f'Exception {e} in file {os.path.basename(__file__)}')
            pass
    """
    Return True if the registry exist
    """
    def register_exists(self, dataReference: str) -> bool:
        reference = db.reference(f'{self.reference}/{dataReference}', self.RTD)
        snapshot = reference.get()
        
        return True if snapshot != None else False
        

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
        
        firebase_admin.initialize_app(cred, {
            'storageBucket': self.bucket_name
            })
        
        log('Firestore storage initialized.')
        
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
    
    def files_listing(self,
                   path: str = PATH_CLOUD_TRAIN) -> list:
        
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix=path)

        temp_files: list = []
        
        for blob in blobs:
            if not str(blob.name).endswith('/'):
                temp_files.append(blob.name)
        
        return temp_files
    
    """
    Returns True if new files are available
    False if no new files are available
    """
    def download_images_stack(self) -> bool:
        start = time.time()
        
        if not os.path.isdir(self.download_path):
            os.mkdir(self.download_path)
        
        if len(self.files_list) <= 0:
            log('No files in memory.\n¿Have you runned FirestoreConnector.files_list()?')
            return
        
        bucket = storage.bucket()
        new_files: list = []
        
        for file in self.files_list:
            filename: str = str(file).split('/')[1]
            
            """
            Check if file was processed.
            """
            if not check_processed('processed.log', file):
                new_files.append(filename)
                blob = bucket.blob(file)
                
                log(f'Downloading: {file}')
                
                """
                Add file into registry of processed files to not re-process
                """
                log(file, 'processed.log', False)
                blob.download_to_filename(os.path.join(self.download_path, filename))
        
        if len(new_files) != 0:
            log(f'Files downloaded in {time.time() - start}')
            return True
        
        return False
        
    def upload_image_stack(self,
                           final_detections_path: str = FINAL_DETECTIONS_PATH,
                           source_path: str = None) -> None:
        start: int = time.time()
        
        if source_path == None:
            source_path = self.detection_path
        
        """
        Files that are in the cloud.
        """
        uploaded_files: list = self.files_listing(source_path)
        uploaded_files = [str(x).split('/')[1] for x in uploaded_files]
        
        for file in os.listdir(final_detections_path):
            if not file in uploaded_files:
                cloud_path: str = os.path.join(source_path + file)
                local_path: str = os.path.join(final_detections_path, file)
                
                bucket = storage.bucket()
                blob = bucket.blob(cloud_path)
                
                try:
                    filename: str = file.split('.')[0]
                    log(f'Uploading {filename}.')
                    blob.upload_from_filename(local_path)
                    os.remove(local_path)
                except Exception as e:
                    msg: str = f'Exception {e}'
                    log(msg)
                    print(msg)
            
        log(f'Files uploaded in {time.time() - start}')
                

