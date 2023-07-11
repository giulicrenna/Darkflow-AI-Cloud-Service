# Darkflow-Weed-AI
---
    
Ubuntu services for continuous object detection with YOLOv8 models and openCV

## Dependencies
---

- python3
- python3-pip
- libgl1-mesa-dev

## Available Models
---
- yolovXn.pt
- yolovXs.pt
- yolovXm.pt
- yolovXl.pt
- yolovXx.pt

## Examples
---

### To train a custom model:
The yaml_path must be the path from the **datasets** folder

```
from src.train_model import train_model

if __name__ == '__main__':
    yaml : str = 'pothole/data.yaml'
    train_name : str = 'baches'
    
    train_model(yaml, train_name)
```

### To predict:

```
if __name__ == '__main__':
    while True:
        try:
            my_model = Predictor(model_name='yolov5xu.pt')
            my_model.keep_prediction() # or my_model.single_prediction()
        except Exception as e:
            if e == KeyboardInterrupt:
                break
            pass
        
```