#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2, masks
import numpy as np 
from geometry_msgs.msg import Twist, Vector3


def filter_color(bgr, low, high):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask  

def center_of_mass(mask):
    M = cv2.moments(mask)
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

def restringir_window_size(img_bgr_limpa, mascara, img_bgr_visivel, list_xo_y0):
    x0 = list_xo_y0[0]
    # y0 = list_xo_y0[1]
    y0 = 90
    x1 = img_bgr_limpa.shape[1] - 10
    y1 = img_bgr_limpa.shape[0] - 20

    clipped = mascara[y0:y1, x0:x1]
    cv2.rectangle(img_bgr_visivel, (x0, y0), (x1, y1), (255,0,0),2,cv2.LINE_AA) #desenha retangulo da área selecionada
    return clipped


def centro_massa_cor(img_bgr_limpa, str_cor, img_bgr_visivel):
    hsv_low, hsv_high = masks.criar_valores_mascaras(str_cor)
    color_mask = filter_color(img_bgr_limpa, hsv_low, hsv_high)

    if str_cor == "amarelo":
        color_mask = restringir_window_size(img_bgr_limpa, color_mask, img_bgr_visivel, [30,60])

    posicao_centro_massa = center_of_mass(color_mask) 
    desenha_centro = crosshair(img_bgr_visivel, posicao_centro_massa, 8, (255,0,255))
    return posicao_centro_massa

def restringir_window_creeper_e_tags(img_bgr_limpa, list_xo_y0):
    x0 = list_xo_y0[0]
    y0 = list_xo_y0[1]
    x1 = img_bgr_limpa.shape[1] - 10
    y1 = img_bgr_limpa.shape[0] - y0

    clipped = img_bgr_limpa[y0:y1, x0:x1]
    # cv2.rectangle(img_bgr_visivel, (x0, y0), (x1, y1), (255,0,0),2,cv2.LINE_AA) #desenha retangulo da área selecionada
    return clipped

def buscar_creeper(img_bgr_limpa, cor_creeper, img_bgr_visivel): 
    hsv_low, hsv_high  = masks.criar_valores_mascaras(cor_creeper)
    is_creeper_visible = False
    color_mask_creeper = filter_color(img_bgr_limpa, hsv_low, hsv_high)
    # cv2.imshow("red mask", color_mask_creeper)

    try: 
        posicao_centro_massa_creeper = center_of_mass(color_mask_creeper) 
        desenha_centro = crosshair(img_bgr_visivel, posicao_centro_massa_creeper, 8, (255,100,100))
        is_creeper_visible = True
        return is_creeper_visible, posicao_centro_massa_creeper
    except:
        return is_creeper_visible, (0,0)


incerteza = 15
centro    = 160

