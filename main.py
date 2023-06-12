import argparse
from src.predictor import Predictor

parser = argparse.ArgumentParser()

parser.add_argument("model")

args = parser.parse_args()

model : str = args.model


if __name__ == '__main__':
    while True:
        try:
            my_model = Predictor(model_name=model)
            my_model.keep_prediction()
        except Exception as e:
            if e == KeyboardInterrupt:
                break
            pass
        
    