#!/bin/bash

sudo apt-get install -y python3 python3-pip
sudo apt-get install -y libgl1-mesa-dev
sudo apt-get install python3.11-venv

mkdir /etc/darkflow_weed

cp -r ./ /etc/darkflow_weed

cp /etc/darkflow_weed/darkflow_weed /bin/

chmod +x /bin/darkflow_weed

cd /etc/darkflow_weed

echo "INSTALANDO DEPENDENCIAS"

pip3 install --break-system-packages --upgrade pip setuptools wheel 
pip3 install git+https://github.com/opencv/opencv-python
pip3 install -r --break-system-packages requirements.txt 

