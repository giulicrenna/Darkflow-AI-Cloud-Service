#!/bin/bash

echo "CREANDO AMBIENTE VIRTUAL" 
python3.11 -m venv env

echo "ACTIVANDO AMBIENTE VIRTUAL"
source env/bin/activate

echo "INSTALANDO DEPENDENCIAS"
pip install -r requirements.txt