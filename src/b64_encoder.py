import base64
import os
import io
from imageio.v2 import imread
import matplotlib.pyplot as plt

FILENAME : str = 'family.jpg'
ABS_PATH : str = os.getcwd()
IMAGE_PATH : str = os.path.join(ABS_PATH, 'media', FILENAME)


def export_b64(img_path: str = IMAGE_PATH, show: bool = False) -> str:
    with open(img_path, 'rb') as file:
        img_data : bytearray = file.read()
    
    b64_bytes = base64.b64encode(img_data)
    b64_string = b64_bytes.decode()

    img = imread(io.BytesIO(base64.b64decode(b64_string)))

    if show:
        plt.figure()
        plt.imshow(img, cmap="gray")
        plt.show()
    
    return b64_string

if __name__ == '__main__':
    data : str = export_b64()
    print(data)
    with open('image_encoded.txt', 'w') as file:
        file.write(data)
        file.close()