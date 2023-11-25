import requests
from b64_encoder import export_b64
from compressor import *

img_text : str = export_b64('./media/tv.png')

protocol : str = 'http'
host : str = 'giuliscloud.duckdns.org'
port: str = '5555'
endpoint : str = 'simple_detection'

if __name__ == '__main__':
    rq = requests.get(f'{protocol}://{host}:{port}/{endpoint}', params={
        'img_data' : img_text
    })
    
    print(rq.text)