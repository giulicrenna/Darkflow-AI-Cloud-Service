#!/bin/bash

apt-get install python3 python3-pip
apt-get install -y libgl1-mesa-dev

mkdir /etc/darkflow_weed

cp -r ./ /etc/darkflow_weed

cp /etc/darkflow_weed/darkflow_weed /bin/

chmod +x /bin/darkflow_weed

cd /etc/darkflow_weed

echo "INSTALANDO DEPENDENCIAS"

pip3 install -r requirements.txt

