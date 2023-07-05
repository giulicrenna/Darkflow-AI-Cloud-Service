import requests
from b64_encoder import export_b64

img : str = export_b64('./media/tv.png')
protocol : str = 'http'
host : str = '127.0.0.1'
port: str = '5555'
endpoint : str = 'simple_detection'

if __name__ == '__main__':
    rq = requests.get(f'{protocol}://{host}:{port}/{endpoint}', params={
        'img_data' : img
    }).text
    
    print(rq)
