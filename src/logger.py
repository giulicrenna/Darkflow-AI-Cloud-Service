import datetime
import os

logs_dir: str = os.path.join(os.getcwd(), 'logs')

"""
Create the logs folder if not exist
"""
if not os.path.isdir(logs_dir):
    os.makedirs(logs_dir)
    
def log(log_entry : str, path: str = 'service.log', add_time: bool = True) -> None:
    date = datetime.datetime.now()
    current_date : str = str(date.hour) + ':' + str(date.minute) + '/' + str(date.day) + '-' + str(date.month)  + '-' + str(date.year)  

    PATH = os.path.join(logs_dir, path)
    
    """
    Write or create the registry
    """
    with open(PATH, 'a') as file:
        if add_time:
            file.write(f'{current_date} -> {log_entry}\n')
        else:
            file.write(f'{log_entry}\n')
        file.close()
        