import numpy as np 
import cv2, math

hsv_amarelo = 30
hsv_blue = 120
hsv_pink = 166
hsv_vermelho = 0 
incerteza = 2

hsvs = {"amarelo" : 30, "blue":120, "pink":166 }


for k,v in hsvs.items():
    a = "low_"
    b = a+k
    print(b)
    
