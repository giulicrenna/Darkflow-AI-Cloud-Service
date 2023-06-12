#!/bin/bash

mkdir /etc/darkflow_weed

cp -r ./ /etc/darkflow_weed

cp /etc/darkflow_weed/darkflow_weed /bin/

chmod +x /bin/darkflow_weed

cd /etc/darkflow_weed

echo "INSTALANDO DEPENDENCIAS"

pip install -r requirements.txt

