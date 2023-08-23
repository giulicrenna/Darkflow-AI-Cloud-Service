FROM ubuntu

RUN apt-get update 
RUN apt-get install -y bash
RUN apt-get install wget -y
RUN apt-get install zip -y
RUN apt-get install python3.11 -y
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install python3-pip python3-dev -y

RUN mkdir downloads

COPY src /service/src
COPY model /service/model
COPY requirements.txt /service/requirements.txt
COPY main.py /service/main.py
COPY json/firebase_key.json /service/firebase_key.json
COPY config.json /service/config.json

WORKDIR /service

RUN pip install -r requirements.txt 

CMD ["uvicorn", "main:run", "--host", "0.0.0.0", "--port", "8000"]