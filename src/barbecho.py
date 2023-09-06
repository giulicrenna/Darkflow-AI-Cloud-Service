import cv2 as cv
import numpy as np
import os
import pandas as pd
import math

DEBUG: bool = False
font = cv.FONT_HERSHEY_SIMPLEX
position = (50, 50)  # Coordinates (x, y) where you want to place the text
font_scale = 2  # Font scale
font_color = (0, 0, 0)  # Font color in BGR format (green in this case)
font_thickness = 7  # Font thickness


def calculate_barbecho_percent(IMAGE_PATH: str) -> dict:
    img = cv.imread(IMAGE_PATH)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV_FULL)
    lower_green = np.array([50,100,50])
    upper_green = np.array([70,255,255])

    mask = cv.inRange(hsv, lower_green, upper_green)
    res = cv.bitwise_and(img, img, mask=mask)
    
    #_, binary_mask = cv.threshold(mask, 1, 255, cv.THRESH_BINARY)

    binary_mask = np.asarray(mask)

    binary_mask = binary_mask.flatten()

    func = np.vectorize(lambda x: 0 if x <= 50 else 255)

    binary_mask = func(binary_mask)

    print(f'BM Shape: {binary_mask.shape}') if DEBUG else ...

    ones: int = np.count_nonzero(binary_mask == 255) # ONE REPRESENT THE PLANT
    zeros: int = np.count_nonzero(binary_mask == 0) # ZERO REPRESENT THE BARBECHO
    nn: int = np.sum((binary_mask != 0) & (binary_mask != 255))

    p: int = (ones/zeros)*100
    
    print(f'W: {ones}\nB: {zeros}\nNN: {nn}') if DEBUG else ...
    print(f'Q: {(ones/zeros)*100}') if DEBUG else ...

    res = cv.resize(mask, (1080, 720))
    img = cv.resize(img, (1080, 720))
    img = cv.putText(img, f'porcentaje de barbecho: {round(p, 1)}%', position, font, font_scale, font_color, font_thickness)
    
    h1, w1 = res.shape[:2]
    h2, w2 = img.shape[:2]

    #create empty matrix
    vis = np.zeros((max(h1, h2), w1+w2,3), np.uint8)

    #combine 2 images
    vis[:h1, :w1, 2] = res
    vis[:h2, w1:w1+w2,:3] = img
    
    cv.imwrite(f'output/{os.path.basename(IMAGE_PATH)}', vis)
    
    if DEBUG:
        cv.imshow("binary_mask", cv.resize(mask, (1080, 720)))
        if cv.waitKey(0):
            cv.destroyAllWindows()
    
    p = 100-p
    
    return {'barbecho_percent' : p}

acumulativa: list = []

"""
for i in os.listdir('img'):
    q: dict = calculate_barbecho_percent(f'img/{i}')
    p: int = 100 - q['barbecho_percent']
    acumulativa.append(p)
    print(f'{i} -> {p}')
    
print(sum(acumulativa)/len(acumulativa))
"""