FROM python:3.8-slim-buster

COPY src .
COPY model .
COPY test_img .
COPY requirements.txt .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install -r requirements.txt

EXPOSE 23444

RUN python3 src/predict_from_cam.py