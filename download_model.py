from ultralytics import YOLO
import os

os.system('clear')

available_models : list = os.listdir('model')

print('Modelos disponibles:')
print('#'*50)
for i in available_models:
    print(f'\t> {i}')

model_name : str = input("\n\nModelo a descargar: ")

print('descargando modelo...')
model = YOLO(f"model/{model_name}")