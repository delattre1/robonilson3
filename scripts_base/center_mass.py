#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2, math
import numpy as np 
from geometry_msgs.msg import Twist, Vector3

# print("Baixe o arquivo a seguir para funcionar: ")
# print("https://github.com/Insper/robot202/raw/master/projeto/centro_massa/line_following.mp4")

# cap = cv2.VideoCapture('line_following.mp4')

# Valores para amarelo usando um color picker
low = np.array([22, 50, 50],dtype=np.uint8)
high = np.array([36, 255, 255],dtype=np.uint8)

def filter_color(bgr, low, high):
    """ REturns a mask within the range"""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    return mask     

# Função centro de massa baseada na aula 02  https://github.com/Insper/robot202/blob/master/aula02/aula02_Exemplos_Adicionais.ipynb
# Esta função calcula centro de massa de máscara binária 0-255 também, não só de contorno
def center_of_mass(mask):
    """ Retorna uma tupla (cx, cy) que desenha o centro do contorno"""
    M = cv2.moments(mask)
    # Usando a expressão do centróide definida em: https://en.wikipedia.org/wiki/Image_moment
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return [int(cX), int(cY)]

def crosshair(img, point, size, color):
    """ Desenha um crosshair centrado no point.
        point deve ser uma tupla (x,y)
        color é uma tupla R,G,B uint8
    """
    x,y = point
    cv2.line(img,(x - size,y),(x + size,y),color,5)
    cv2.line(img,(x,y - size),(x, y + size),color,5)

def center_of_mass_region(mask, x1, y1, x2, y2):
    # Para fins de desenho
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    clipped = mask[y1:y2, x1:x2]
    c = center_of_mass(clipped)
    c[0]+=x1
    c[1]+=y1
    crosshair(mask_bgr, c, 10, (0,0,255))
    cv2.rectangle(mask_bgr, (x1, y1), (x2, y2), (255,0,0),2,cv2.LINE_AA)
    return mask_bgr

def seleciona_window_centro_de_massa(img_bgr):
    global vel 
    low_yellow, high_yellow = np.array([22, 50, 50],dtype=np.uint8), np.array([36, 255, 255],dtype=np.uint8)
    yellow_mask = filter_color(img_bgr, low_yellow, high_yellow)
    #selecionar window
    x0 = 0
    y0 = 40
    x1 = img_bgr.shape[1]
    # print('é a metade: {}'.format(x1/2))
    y1 = img_bgr.shape[0] - y0
    clipped = yellow_mask[y0:y1, x0:x1]
    try: 
        posicao_centro_massa = center_of_mass(clipped) 
        desenha_centro = crosshair(img_bgr, posicao_centro_massa, 20, (255,0,255))
        cv2.rectangle(img_bgr, (x0, y0), (x1, y1), (255,0,0),2,cv2.LINE_AA) #desenha retangulo da área selecionada

    except:
        print('falha ao selecionar estrada')
    return img_bgr, posicao_centro_massa

def rotacao_conforme_centro_pista(centro_massa):
    x_centro = centro_massa[0]
    incerteza = 20
    centro = 160
    lin = 0.04
    if x_centro < centro - incerteza: #meio é 160
        # print("tem que girar pra esquerda (+vel_ang)")
        return "virar esquerda"
    elif x_centro > centro + incerteza:
        return "virar direita"
        # print("tem que virar pra direita (-vel ang) ")
    else:
        return "seguir reto"

