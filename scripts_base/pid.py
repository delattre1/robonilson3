#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2, masks
import numpy as np 
from geometry_msgs.msg import Twist, Vector3

from encontra_centro_massa import * 

str_cor = "amarelo"

low_threshold=50
high_threshold=150

x0, y0 = 70, 150
centro_x_tela = 160
tamanho_tela_y = 240

def window_yellow_line(img_bgr_limpa, img_bgr_visivel):
    x1 = img_bgr_limpa.shape[1] - x0
    y1 = img_bgr_limpa.shape[0] - 10

    clipped = img_bgr_limpa[y0:y1, x0:x1]
    cv2.rectangle(img_bgr_visivel, (x0, y0), (x1, y1), (255,120,120),2,cv2.LINE_AA) #desenha retangulo da área selecionada
    return clipped

def derivada_estrada(x, y):
    return ((x-centro_x_tela)/(tamanho_tela_y-y))

def cria_linha_caminho(img_bgr_limpa, str_cor, img_bgr_visivel):
    hsv_low, hsv_high = masks.criar_valores_mascaras(str_cor)

    estrita_window = window_yellow_line(img_bgr_limpa, img_bgr_visivel)

    color_mask = filter_color(estrita_window, hsv_low, hsv_high)

    try:
        cm_xy = center_of_mass(color_mask)
    except:
        cm_xy = (0,0)

    if cm_xy != (0,0):
        cm_xy[0] += x0
        cm_xy[1] += y0
        crosshair(img_bgr_visivel, cm_xy, 4, (120,44,255))

        erro_x = cm_xy[0] - centro_x_tela
        tg_alfa = derivada_estrada(cm_xy[0], cm_xy[1])

        print(erro_x)
        print(tg_alfa)

    cv2.imshow("mask Estrada", color_mask)

