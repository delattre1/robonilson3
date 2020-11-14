#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2, masks, math
import numpy as np 
from geometry_msgs.msg import Twist, Vector3

str_cor = "amarelo"
low_threshold=50
high_threshold=150

x0, y0 = 70, 100
centro_x_tela = 160
tamanho_tela_y = 240


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
    x,y = point
    cv2.line(img,(x - size,y),(x + size,y),color,5)
    cv2.line(img,(x,y - size),(x, y + size),color,5)

def window_yellow_line(img_bgr_limpa, img_bgr_visivel):
    x1 = img_bgr_limpa.shape[1] - x0
    y1 = img_bgr_limpa.shape[0]

    clipped = img_bgr_limpa[y0:y1, x0:x1]
    cv2.rectangle(img_bgr_visivel, (x0, y0), (x1, y1), (255,120,120),2,cv2.LINE_AA) #desenha retangulo da área selecionada
    return clipped

def derivada_estrada(x, y):
    return (float(x-centro_x_tela)/(tamanho_tela_y-y))

def encontra_direcao_ate_cm(img_bgr_limpa, str_cor, img_bgr_visivel):
    hsv_low, hsv_high = masks.criar_valores_mascaras(str_cor)

    if str_cor == "amarelo":
        estrita_window = window_yellow_line(img_bgr_limpa, img_bgr_visivel)
        color_mask = filter_color(estrita_window, hsv_low, hsv_high)
    
    else:
        color_mask = filter_color(img_bgr_limpa, hsv_low, hsv_high)

    try:
        cm_xy = center_of_mass(color_mask)
    except:
        return None, None

    if str_cor == "amarelo":
        cm_xy[0] += (x0)
        cm_xy[1] += (y0)
    crosshair(img_bgr_visivel, cm_xy, 4, (120,44,255))

    erro_x = (cm_xy[0] - centro_x_tela)
    tg_alfa = derivada_estrada(cm_xy[0], cm_xy[1])
    alfa = math.atan(tg_alfa)
    sin_alfa = math.sin(alfa)
    return erro_x, tg_alfa  

kp = 0.003 #constante erro
kd = 10    #constante derivada

def altera_velociade(velocidade_atual, erro_x, tg_alfa):
    if tg_alfa is not None:
        change_in_velocity = -kp*(erro_x + kd*tg_alfa) + 0.002
        velocidade_atual.angular.z = change_in_velocity #- (velocidade_atual.angular.z*0.1)
        vel_lin = (.8 - abs(change_in_velocity)) + (1/abs(change_in_velocity))*1e-3
        print(vel_lin)
        velocidade_atual.linear.x  =  vel_lin
    
    return velocidade_atual