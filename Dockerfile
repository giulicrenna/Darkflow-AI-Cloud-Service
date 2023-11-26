FROM ubuntu

RUN apt-get update --fix-missing -y 
RUN apt-get install -y bash
RUN apt-get install wget -y
RUN apt-get install zip -y
RUN apt-get install python3.11 -y
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install python3-pip python3-dev -y

COPY . /service/

WORKDIR /service

RUN pip install -r requirements.txt 

# uvicorn main:run --host 0.0.0.0 --port 8000
CMD ["uvicorn", "main:run", "--host", "0.0.0.0", "--port", "80"]