from ultralytics import YOLO
import torch

import os
import socket
import json
import time
import calendar

import supervision as sv
import cv2
import numpy as np
import paho.mqtt.client as mqtt
import uuid

import io
import base64
from imageio.v2 import imread
from PIL import Image, ImageFile

from src.logger import log

ImageFile.LOAD_TRUNCATED_IMAGES = True

ABS_PATH : str = os.getcwd()
SAVE_PATH : str = 'detections/'
class Predictor:
    def __init__(self,
                 camera_port : int = 0,
                 model_name : str = "darkflow-weed-yolov8l.pt",
                 mqtt_address : str = "test.mosquitto.org",
                 mqtt_topic : str = "darkflowtest",
                 mqtt_port : int = 1883,
                 tcp_port : int = 25400,
                 show : bool = False,
                 save_predictions : bool = True,
                 save_with_bbox  : bool = True,
                 save_both : bool = True,
                 use_mqtt : bool = False,
                 use_tcp :bool = False) -> None:
        
        self.camera_port : int = camera_port
        self.model_name : str = model_name
        self.mqtt_address : str = mqtt_address
        self.mqtt_topic : str = mqtt_topic
        self.mqtt_port : int = mqtt_port
        self.tcp_port : int = tcp_port
        self.show : bool = show
        self.save_predictions : bool = save_predictions
        self.save_with_bbox : bool = save_with_bbox
        self.save_both : bool = save_both
        self.use_mqtt : bool = use_mqtt
        self.use_tcp : bool = use_tcp
        
        self.flag = True
        
        log(f'Initializing {os.path.basename(__file__)}.')
        
        #log(f'Iniciando Predictor con parámetros:\n\t-camera_port:{camera_port}\n\t-model_name:{model_name} \
        #    \n\t-mqtt_address:{mqtt_address}\n\t-mqtt_topic:{mqtt_topic}\n\t-mqtt_port:{mqtt_port}\n\t-tcp_port:{tcp_port}\n')
        
        os.makedirs(SAVE_PATH) if not os.path.exists(SAVE_PATH) else ...
        
        if self.use_mqtt:
            self.mqtt_client : object = self.setup_mqtt()
        if self.use_tcp:
            self.tcp_client : object = self.setup_tcp_socket() 
        
        self.predictor_model : object = self.load_model()
        
    def load_model(self) -> object:
        try:
            log(f'Loading model {self.model_name}')
            
            device: str = "mps" if torch.backends.mps.is_available() else "cpu"
            
            log(f'Available device: {device}')
            
            model = YOLO(f'{ABS_PATH}/model/{self.model_name}')
            model.to(device)
        
            return model
        
        except Exception as e:
            print(f'No se pudo cargar el modelo, código de error:\n{e}')
            return None
        
    def setup_mqtt(self) -> object:
        print(f'Configurando servidor MQTT con host: {self.mqtt_address}')
        try:
            client : object = mqtt.Client()
            client.on_connect = self.on_connect

            client.connect(self.mqtt_address, self.mqtt_port, 60)

            return client
        except Exception as e:
            print(f'No se pudo conectar al servidor, con código de error:\n {e}')
            return None
            
    def on_connect(self, client, userdata, flags, rc) -> None:
        print("Conectado con código: " + str(rc))    

    def publish(self, message : str = '\{\}') -> None:
        if self.mqtt_client != None:
            self.mqtt_client.publish(self.mqtt_topic, message)
    
    def setup_tcp_socket(self) -> object:
        ...
        
    def send_tcp_message(self, message : str = '\{\}') -> object:
        ...
    
    def predict_from_b64(self, b64_image: str,
                         filename = str(uuid.uuid4()),
                         extra_data: dict = {}) -> str:
        img = imread(io.BytesIO(base64.b64decode(b64_image)))
        
        frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        result : YOLO = self.predictor_model.predict(frame,
                            agnostic_nms=True,
                            verbose=False)[0]
        
        detections = sv.Detections.from_yolov8(result)
        
        labels = [
            f"{self.predictor_model.model.names[class_id]}_{confidence:0.2f}"
            for _, confidence, class_id, _
            in detections
         ]
        single_labels : list = [
            f"{self.predictor_model.model.names[class_id]}"
            for _, class_id, class_id, _
            in detections
        ]
        if len(single_labels) == 0:
            single_labels = ['None']
        data : dict = {
            'timestamp' : calendar.timegm(time.gmtime()),
            'detected_labels' : single_labels
        } 
        object_metadata : list = []
        
        for i, box in enumerate(detections.xyxy.tolist()):
            xmin, ymin, xmax, ymax = box
            bbox : dict = {
                'x1' : round(xmin),
                'y1' : round(ymin),
                'x2' : round(xmax),
                'y2' : round(ymax)
            } 
            confidence : int = labels[i].split('_')[1]
            object_data : dict = {
                'object_name' : single_labels[i],
                'confidence' : confidence,
                'bbox' : bbox
            }
            object_metadata.append(object_data)

        if len(object_metadata) == 0:
            object_metadata = ['None']
        
        data['metadata'] = object_metadata                                    
        
        FILENAME: str = filename
                        
        """
        <... and not 'None' in single_labels>
        This prevents the creation and upload of images without predictions
        """
        if self.save_predictions and not 'None' in single_labels:
            if self.save_both:
                FILENAME_ = FILENAME + '_nbbox'
                cv2.imwrite(os.path.join(SAVE_PATH, f'{FILENAME_}.png'), frame)
                
            if self.save_with_bbox:
                FILENAME_ = FILENAME + '_bbox'
                box_annotator = sv.BoxAnnotator(
                                    thickness=5,
                                    text_thickness=5,
                                    text_scale=2
                                )

                frame_ = box_annotator.annotate(
                    scene=frame, 
                    detections=detections, 
                    labels=labels
                )
                
                frame = cv2.resize(frame, (1080, 720))
                cv2.imwrite(os.path.join(SAVE_PATH, f'{FILENAME_}.png'), frame_)
                
            else:
                FILENAME_ = FILENAME + '_nbbox'
                MULT: int = 1.5
                frame = cv2.resize(frame, (1080*MULT, 720*MULT))
                cv2.imwrite(os.path.join(SAVE_PATH, f'{FILENAME_}.png'), frame)
                
        data_json : str = json.dumps(data, indent=2)
        self.publish(data_json) if self.use_mqtt else ...
        
        for key, value in extra_data.items():
           data[key] = value
        
        #For testing purposes
        #log(f'{filename}:{detections}')
        
        return data
    
    def single_prediction(self) -> dict:
        cap = cv2.VideoCapture(self.camera_port)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        ret, frame = cap.read()
        result = self.predictor_model(frame,
                            agnostic_nms=True)[0]
        
        detections = sv.Detections.from_yolov8(result)
        
        labels = [
            f"{self.predictor_model.model.names[class_id]} {confidence:0.2f}"
            for _, confidence, class_id, _
            in detections
         ]
        
        single_labels : list = [
            f"{self.predictor_model.model.names[class_id]}"
            for _, class_id, class_id, _
            in detections
        ]
        
        # print(f'{len(single_labels)} - {len(detections.xyxy.tolist())}')
        data : dict = {
            'timestamp' : calendar.timegm(time.gmtime()),
            'detected_labels' : single_labels
        } 
        
        object_metadata : list = []
        
        for i, box in enumerate(detections.xyxy.tolist()):
                xmin, ymin, xmax, ymax = box
                bbox : dict = {
                    'xmin' : round(xmin, 1),
                    'ymin' : round(ymin, 1),
                    'xmax' : round(xmax, 1),
                    'ymax' : round(ymax, 1)
                } 
                
                confidence : int = labels[i].split(' ')[1]
                
                object_data : dict = {
                    'object_name' : single_labels[i],
                    'confidence' : confidence,
                    'bbox' : bbox
                }
                
                object_metadata.append(object_data)

                data[f'metadata'] = object_metadata                
                    
        data_json : str = json.dumps(data, indent=2)
        FILENAME: str = str(data['timestamp'])
                        
        if self.save_predictions:
            if self.save_both:
                FILENAME_ = FILENAME + '_nbbox'
                cv2.imwrite(os.path.join(SAVE_PATH, f'{FILENAME_}.png'), frame)
                
            if self.save_with_bbox:
                FILENAME_ = FILENAME + '_bbox'
                box_annotator = sv.BoxAnnotator(
                                    thickness=1,
                                    text_thickness=1,
                                    text_scale=1
                                )

                frame_ = box_annotator.annotate(
                    scene=frame, 
                    detections=detections, 
                    labels=labels
                )
                cv2.imwrite(os.path.join(SAVE_PATH, f'{FILENAME_}.png'), frame_)
                
            else:
                FILENAME_ = FILENAME + '_nbbox'
                cv2.imwrite(os.path.join(SAVE_PATH, f'{FILENAME_}.png'), frame)
                
            with open(os.path.join(SAVE_PATH, f'{FILENAME}.json'), 'w+') as file:
                file.write(data_json)
            
        self.publish(data_json) if self.use_mqtt else ...
            
        return data
    
    def keep_prediction(self) -> None:
        cap = cv2.VideoCapture(self.camera_port)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if self.show:
            box_annotator = sv.BoxAnnotator(
                                    thickness=2,
                                    text_thickness=2,
                                    text_scale=1
                                )
        while self.flag:
            ret, frame = cap.read()
            result = self.predictor_model(frame,
                                agnostic_nms=True)[0]
            
            detections = sv.Detections.from_yolov8(result)
            
            labels = [
                f"{self.predictor_model.model.names[class_id]} {confidence:0.2f}"
                for _, confidence, class_id, _
                in detections
            ]
            
            single_labels : list = [
                f"{self.predictor_model.model.names[class_id]}"
                for _, class_id, class_id, _
                in detections
            ]
            
            for i, label in enumerate(single_labels):
                single_labels[i] = label + f'_{i}'
            
            data : dict = {
                'timestamp' : calendar.timegm(time.gmtime()),
                'detected_labels' : single_labels
            } 
            
            object_metadata : list = []
            
            for i, box in enumerate(detections.xyxy.tolist()):
                xmin, ymin, xmax, ymax = box
                bbox : dict = {
                    'xmin' : round(xmin, 1),
                    'ymin' : round(ymin, 1),
                    'xmax' : round(xmax, 1),
                    'ymax' : round(ymax, 1)
                } 
                
                confidence : int = labels[i].split(' ')[1]
                
                object_data : dict = {
                    'object_name' : single_labels[i],
                    'confidence' : confidence,
                    'bbox' : bbox
                }
                
                object_metadata.append(object_data)

                data[f'metadata'] = object_metadata                
                    
                    
                data_json : object = json.dumps(data)
                
                 
            if self.show or self.save_predictions:
                box_annotator = sv.BoxAnnotator(
                                    thickness=2,
                                    text_thickness=2,
                                    text_scale=1
                                )
                
                frame = box_annotator.annotate(
                    scene=frame, 
                    detections=detections, 
                    labels=labels
                ) 
                    
                cv2.imwrite(SAVE_PATH, frame) if self.save_predictions else ...
                
                cv2.imshow("yolov8", frame) if self.show else ...

                self.publish(data_json) if self.use_mqtt else ...

                if (cv2.waitKey(30) == 27): 
                    break
                
        if self.show:
            cap.release()
            cv2.destroyAllWindows()
        
"""
if __name__ == '__main__':
    pred = Predictor(model_name='yolov5su.pt')
    pred.keep_prediction()
"""