import os
from src.logger import log

logs_path: str = os.path.join(os.getcwd(), 'logs')

"""
check_processed() -> bool
Return True if file in registry
Return False if file not in registry
"""
def check_processed(data_chunk: str, file: str) -> bool:
    FILE_PATH: str = os.path.join(logs_path, data_chunk)
    
    try:
        with open(FILE_PATH, 'r+') as log_:
            """
            Read lines of file and remove new lines character from them
            """
            lines: list = log_.readlines()
            chunk: set = set([line.strip() for line in lines])
            
            if file in chunk:
                log_.close()
                return True
    except FileNotFoundError:
        log(f'Data chunk: {data_chunk} was not found.')
        return False
    
    return False 
        
        