#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2, math
from pid2 import encontra_direcao_ate_cm, altera_velociade, is_creeper_visible
from tags_id import should_rotacionar_to_find_creeper, distance_creeper

vel_ang = math.pi/15

def rotacionar_no_inicio(estado, velocidade, cor_do_creeper):
    vel_z = 2*vel_ang
    tempo_rotacao_inicio = (math.pi/2)/ vel_z

    if cor_do_creeper == "blue":
        velocidade.angular.z = +vel_z

    elif cor_do_creeper == "vermelho":
        velocidade.angular.z = -vel_z
    return estado, velocidade, tempo_rotacao_inicio
    
def anda_rapidamente_pista(estado, velocidade, img_bgr_limpa, str_cor, img_bgr_visivel):
    erro_x, tg_alfa = encontra_direcao_ate_cm(img_bgr_limpa, str_cor, img_bgr_visivel)
    velocidade = altera_velociade(velocidade, erro_x, tg_alfa, estado)
    return estado, velocidade

def deve_dar_meia_volta(estado, temp_image, imagem_figuras_desenhadas):
    if  should_rotacionar_to_find_creeper(temp_image, imagem_figuras_desenhadas):
        estado = "dar meia volta"
    return estado

def rodar_until_creeper_located(estado, velocidade, temp_image, imagem_figuras_desenhadas, cor_do_creeper):
    velocidade.linear.x  = 0
    velocidade.angular.z = -2*vel_ang

    if is_creeper_visible(temp_image, cor_do_creeper, imagem_figuras_desenhadas)[0] != None:
        estado = "go_to_creeper"
        velocidade.linear.x  = 0
        velocidade.angular.z = 0
    return estado, velocidade

def parar_frente_creeper(estado, velocidade):
    vx = velocidade.linear.x 
    if vx > 0:
        velocidade.linear.x -= 0.01
    else:
        velocidade.linear.x = 0.01
        estado = "capturar creeper"

    velocidade.angular.z = 0

    return estado, velocidade

def endireitar_depois_de_pegar_creeper(estado, velocidade, cor_do_creeper):
    if cor_do_creeper == "pink":
        velocidade.angular.z = 2*vel_ang
        velocidade.linear.x  = 0.1
        vz = velocidade.angular.z
        time_rodar_after_pegar_creeper = (math.pi) / vz
    elif cor_do_creeper == "blue":
        velocidade.angular.z = -2*vel_ang
        velocidade.linear.x  = 0.3
        vz = abs(velocidade.angular.z)
        time_rodar_after_pegar_creeper = (math.pi/4) / vz
    else:
        estado = "voltar pra pista"
    return estado, velocidade, time_rodar_after_pegar_creeper