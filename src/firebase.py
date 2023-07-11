import os
import pyrebase
import uuid
import requests
#import firebase_admin
#from firebase_admin import credentials

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
                 train_path: str = PATH_CLOUD_TRAIN,
                 detection_path: str = PATH_CLOUD_TRAIN,
                 download_path: str = DOWNLOAD_PATH) -> None:
            
        self.firebase_config = firebase_config
        self.train_path = train_path
        self.detection_path = detection_path
        self.download_path = download_path
        
        self.firebase: object = pyrebase.initialize_app(config=self.firebase_config)
        self.storage: object = self.firebase.storage()

        self.files_list: list = []
        
    def update_files_list(self,
                   path: str = PATH_CLOUD_TRAIN) -> list:
        files = self.storage.child(path).list_files()
        
        for file in files:
            filename: str = file.name
            
            file_abs: str = str(filename).split('/')[0] + '/'
            
            fileurl: str = self.storage.child(filename).get_url(None)
            
            if file_abs == path:
                self.files_list.append((filename, fileurl))
            
        return self.files_list
    
    def download_images_stack(self) -> None:
        if len(self.files_list) <= 0:
            print('No files in memory.\n¿Have you runned FirestoreConnector.files_list()?')
            return
        
        for file in self.files_list:
            filename: str = str(file[0]).split('/')[1] + '.jpeg'
            
            # response = requests.get(file[1])
            # print(os.path.join(self.download_path, filename))
            # with open(os.path.join(self.download_path, filename), "wb") as f:
            #     f.write(response.content)
            
            self.storage.child(file[0]).download(self.download_path,
                                                 filename)

    def upload_image_stack(self,
                           final_detections_path: str = FINAL_DETECTIONS_PATH,
                           source_path: str = None) -> None:
        if source_path == None:
            source_path = self.detection_path
            
        for file in os.listdir(final_detections_path):
            self.storage.child(file).put(str(uuid.uuid4()))
                

