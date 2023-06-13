import os
import socket
import json

from ultralytics import YOLO
import supervision as sv
import cv2
import numpy as np

import paho.mqtt.client as mqtt


ABS_PATH : str = os.getcwd()

class Predictor:
    def __init__(self,
                 camera_port : str = '0',
                 model_name : str = "darkflow-weed-yolov8l.pt",
                 mqtt_address : str = "test.mosquitto.org",
                 mqtt_topic : str = "darkflowtest",
                 mqtt_port : int = 1883,
                 tcp_port : int = 25400,
                 show : bool = False) -> None:
        
        self.camera_port = camera_port
        self.model_name = model_name
        self.mqtt_address = mqtt_address
        self.mqtt_topic = mqtt_topic
        self.mqtt_port = mqtt_port
        self.tcp_port = tcp_port
        self.show = show
        
        self.parse_args()    
        
        print(f'Iniciando Predictor con parámetros:\n\t-camera_port:{camera_port}\n\t-model_name:{model_name} \
            \n\t-mqtt_address:{mqtt_address}\n\t-mqtt_topic:{mqtt_topic}\n\t-mqtt_port:{mqtt_port}\n\t-tcp_port:{tcp_port}\n')
          
        self.mqtt_client : object = self.setup_mqtt()
        self.predictor_model : object = self.load_model()
        
        self.flag = True
        
    def parse_args(self) -> None:
        if self.camera_port == 'None':
            self.camera_port = 0
        elif self.camera_port in ['0', '1', '2', '3', '4']:
            self.camera_port = int(self.camera_port)
            
        if self.model_name == 'None':
            self.model_name = 'darkflow-weed-yolov8l.pt'
            
        if self.mqtt_address == 'None':
            self.mqtt_address = 'test.mosquitto.org'
            
        if self.mqtt_topic == 'None':
            self.mqtt_topic = 'darkflowtest'
            
        if self.mqtt_port == 'None':
            self.mqtt_port = 1883
            
        if self.tcp_port == 'None':
            self.tcp_port = 25400
    
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
    
    def setup_tcp_socket(self) -> object:
        ...
        
    def send_tcp_message(self, message : str = '\{\}') -> object:
        ...
    
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
                f"{self.predictor_model.model.names[class_id]}-{confidence:0.2f}"
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
                'detected_labels' : single_labels,
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
                
                confidence : int = labels[i].split('-')[1]
                
                object_data : dict = {
                    'object_name' : single_labels[i],
                    'confidence' : confidence,
                    'bbox' : bbox
                }
                
                object_metadata.append(object_data)

            data[f'metadata'] = object_metadata                
                
                
            data_json : object = json.dumps(data)
            
            if self.show:
                
                frame = box_annotator.annotate(
                    scene=frame, 
                    detections=detections, 
                    labels=labels
                ) 
                cv2.imshow("yolov8", frame)

                if (cv2.waitKey(30) == 27): 
                   break
            
            self.publish(data_json)

        if self.show:
            cap.release()
            cv2.destroyAllWindows()
        
"""
if __name__ == '__main__':
    pred = Predictor(model_name='yolov5su.pt')
    pred.keep_prediction()
"""