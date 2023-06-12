import os
import json

from ultralytics import YOLO
import supervision as sv
import cv2
import numpy as np

import paho.mqtt.client as mqtt


ABS_PATH : str = os.getcwd()

class Predictor:
    def __init__(self,
                 camera_port : int = 0,
                 model_name : str = "darkflow-weed-yolov8l.pt",
                 mqtt_address : str = "test.mosquitto.org",
                 mqtt_topic : str = "darkflowtest",
                 mqtt_port : int = 1883,
                 tcp_port : int = 25400) -> None:
        
        self.camera_port = camera_port
        self.model_name = model_name
        self.mqtt_address = mqtt_address
        self.mqtt_topic = mqtt_topic
        self.mqtt_port = mqtt_port
        self.tcp_port = tcp_port
        
        self.mqtt_client : object = self.setup_mqtt()
        self.predictor_model : object = self.load_model()
        
        self.flag = True
        
    def load_model(self) -> object:
        try:
            print(f'Cargando modelo {self.model_name}')
            model = YOLO(f'{ABS_PATH}/model/{self.model_name}')
        
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
    
    def single_prediction(self) -> None:
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
        
        data : dict = {
            'detected_labels' : single_labels,
        } 
        
        for i, box in enumerate(detections.xyxy.tolist()):
            xmin, ymin, xmax, ymax = box
            bbox : dict = {
                'xmin' : xmin,
                'ymin' : ymin,
                'xmax' : xmax,
                'ymax' : ymax
            } 
            
            data[f'box_for_{single_labels[i]}_id_{i}'] = bbox
            
        data_json : object = json.dumps(data)
        
        self.publish(data_json)
    
    def keep_prediction(self) -> None:
        cap = cv2.VideoCapture(self.camera_port)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

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
            
            data : dict = {
                'detected_labels' : single_labels,
            } 
            
            for i, box in enumerate(detections.xyxy.tolist()):
                xmin, ymin, xmax, ymax = box
                bbox : dict = {
                    'xmin' : xmin,
                    'ymin' : ymin,
                    'xmax' : xmax,
                    'ymax' : ymax
                } 
                
                data[f'box_for_{single_labels[i]}_id_{i}'] = bbox
                
            data_json : object = json.dumps(data)
            
            self.publish(data_json)

        
        
