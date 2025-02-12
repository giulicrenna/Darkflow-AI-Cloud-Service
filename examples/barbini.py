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
folder_name : str = "test"
conf : int = 0.25  

if model_name not in available_models:
    print('Modelo Inexistente')
else:
    model = YOLO(f"model/{model_name}")


results = model.predict(source=folder_name,
                        show=False,
                        save=True,
                        conf=conf)
print(results)