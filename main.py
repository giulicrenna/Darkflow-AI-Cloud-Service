import argparse
from src.predictor import Predictor

parser = argparse.ArgumentParser(description='Prediction configuration.')

parser.add_argument('-m', '--model')
parser.add_argument('-c', '--camera_port')
parser.add_argument('-a', '--mqtt_address')
parser.add_argument('-mp', '--mqtt_topic')
parser.add_argument('-p', '--mqtt_port')
parser.add_argument('-tp', '--tcp_port')

args = parser.parse_args()

model : str = args.model
camera_port : str = args.camera_port
mqtt_address : str = args.mqtt_address
mqtt_topic : str = args.mqtt_topic
mqtt_port : str = args.mqtt_port
tcp_port : str = args.tcp_port
    
if __name__ == '__main__':
    while True:
        try:
            Predictor(model_name=model,
                      camera_port=camera_port,
                      mqtt_address=mqtt_address,
                      mqtt_topic=mqtt_topic,
                      mqtt_port=int(mqtt_port),
                      tcp_port=int(tcp_port))    
                
            my_model = Predictor(model_name=model)
            my_model.keep_prediction()
        except Exception as e:
            if e == KeyboardInterrupt:
                break
            pass
        
    