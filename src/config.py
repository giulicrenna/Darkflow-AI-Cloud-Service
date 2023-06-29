import json
import os

ABS_PATH : str = os.getcwd()
file_name : str = 'config.json'
file_path : str = os.path.join(ABS_PATH, file_name)

def get_config() -> dict:
    configs : dict = {}
    
    try:
        if not os.path.exists(file_path):
            print(f'{file_path} No es una ruta válida.')
            raise Exception
        
        configs = json.loads(open(file_path).read())    
    
    except Exception as e:
        print(e)
        
    return configs