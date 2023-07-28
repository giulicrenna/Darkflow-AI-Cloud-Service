FROM debian

RUN apt-get update && apt-get install -y bash
RUN apt-get install wget -y
RUN apt-get install imagemagick -y
RUN apt-get install zip -y
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN aptget install python3.11 -y

COPY src /service/src
COPY model /service/model
COPY requirements.txt /service/requirements.txt
COPY main.py /service/main.py

WORKDIR /service

RUN pip install -r requirements.txt

RUN python3.11 main.py