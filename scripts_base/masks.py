import numpy as np 
import cv2, math

hsv_amarelo = 30
hsv_blue = 120
hsv_pink = 166
hsv_vermelho = 0 
incerteza = 8

hsvs = {"amarelo" : 30, "blue":120, "pink":166, "vermelho":0 }
dic_mascaras = {}

def criar_valores_mascaras(color):
    a = "low_"
    b = "high_"
    
    for k,v in hsvs.items():
        mask_high = b+k
        mask_low = a+k

        if color == "vermelho":
            dic_mascaras[mask_low]  = np.array([0, 150, 150], dtype=np.uint8)
            dic_mascaras[mask_high] = np.array([10, 255, 255], dtype=np.uint8)
        else:
            dic_mascaras[mask_low] = np.array([v-incerteza, 150, 150], dtype=np.uint8)
            dic_mascaras[mask_high] = np.array([v+incerteza, 255, 255], dtype=np.uint8)

    mask_high = b+color
    mask_low  = a+color

    return dic_mascaras[mask_low], dic_mascaras[mask_high]

# usage example 
#print(criar_valores_mascaras('vermelho'))

