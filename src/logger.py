import datetime
import os

PATH = os.path.join(os.getcwd(), 'api.log')

def log(log_entry : str) -> None:
    date = datetime.datetime.now()
    current_date : str = str(date.hour) + ':' + str(date.minute) + '/' + str(date.day) + '-' + str(date.month)  + '-' + str(date.year)  

    with open(PATH, 'a+') as file:
        file.write(f'{current_date} -> {log_entry}\n')
        file.close()
        