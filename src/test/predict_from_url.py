from ultralytics import YOLO
from PIL import Image
import cv2
import os

os.system('cls')

available_models : list = os.listdir('model')

print('Modelos disponibles:')
print('#'*50)
for i in available_models:
    print(f'\t> {i}')

model_name : str = input("\n\nModelo a seleccionar: ")
url : str = input('url: ')
conf : int = 0.25  

if model_name not in available_models:
    print('Modelo Inexistente')
else:
    model = YOLO(f"model/{model_name}")

if __name__ == '__main__':
    results = model.predict(source=url,
                            show=True,
                            save=True,
                            conf=conf,
                            )
    print(results)
    
    
"""
https://www.jardineros.mx/site/qanda/135623/1924/1924_croped.jpg


"""