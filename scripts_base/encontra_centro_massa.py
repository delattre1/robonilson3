#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2, masks
from geometry_msgs.msg import Twist, Vector3


def filter_color(bgr, low, high):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
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

def restringir_window_size(img_bgr_limpa, mascara, img_bgr_visivel):
    x0 = 30
    y0 = 60
    x1 = img_bgr_limpa.shape[1] - 10
    y1 = img_bgr_limpa.shape[0] - y0

    clipped = mascara[y0:y1, x0:x1]
    cv2.rectangle(img_bgr_visivel, (x0, y0), (x1, y1), (255,0,0),2,cv2.LINE_AA) #desenha retangulo da área selecionada
    return clipped


def centro_massa_cor(img_bgr_limpa, str_cor, img_bgr_visivel):
    hsv_low, hsv_high = masks.criar_valores_mascaras(str_cor)
    color_mask = filter_color(img_bgr_limpa, hsv_low, hsv_high)

    if str_cor == "amarelo":
        color_mask = restringir_window_size(img_bgr_limpa, color_mask, img_bgr_visivel)

    posicao_centro_massa = center_of_mass(color_mask) 
    desenha_centro = crosshair(img_bgr_visivel, posicao_centro_massa, 8, (255,0,255))
    return posicao_centro_massa

def direcao_centro_massa_cor_escolhida(img_bgr_limpa, str_cor, img_bgr_visivel):
    try:
        cm = centro_massa_cor(img_bgr_limpa, str_cor, img_bgr_visivel)
        x_centro  = cm[0]

        if x_centro < centro - incerteza:
            return "virar esquerda"
        elif x_centro > centro + incerteza:
            return "virar direita"
        else:
            return "seguir reto"

    except:
        return "perdeu pista"

def movimenta_to_centro_massa(qual_direcao, velocidade_atual, vel_lin, vel_ang):
    if   qual_direcao == "seguir reto":
        velocidade_atual.angular.z = 0
        if velocidade_atual.linear.x <= 2*vel_lin:
            velocidade_atual.linear.x += 0.1*vel_lin
        return velocidade_atual

    elif qual_direcao == "virar direita":
        velocidade_atual.angular.z = -vel_ang
        return velocidade_atual

    elif qual_direcao == "virar esquerda":
        velocidade_atual.angular.z = vel_ang
        return velocidade_atual

    elif qual_direcao == "perdeu pista":
        velocidade_atual.linear.x = 0
        velocidade_atual.angular.z = -2*vel_ang
        return velocidade_atual

def buscar_creeper(img_bgr_limpa, cor_creeper, img_bgr_visivel): 
    hsv_low, hsv_high  = masks.criar_valores_mascaras(cor_creeper)
    is_creeper_visible = False
    color_mask_creeper = filter_color(img_bgr_limpa, hsv_low, hsv_high)
    try: 
        posicao_centro_massa_creeper = center_of_mass(color_mask_creeper) 
        desenha_centro = crosshair(img_bgr_visivel, posicao_centro_massa_creeper, 8, (255,100,100))
        is_creeper_visible = True
        return is_creeper_visible, posicao_centro_massa_creeper
    except:
        return is_creeper_visible, (0,0)

def move_to_creeper(posicao_centro_massa_creeper):
    try:
        x_centro  = posicao_centro_massa_creeper[0]

        if x_centro < centro - incerteza:
            return "virar esquerda"
        elif x_centro > centro + incerteza:
            return "virar direita"
        else:
            return "seguir reto"

    except:
        return "perdeu pista"

incerteza = 15
centro    = 160
