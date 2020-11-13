#!/usr/bin/python
# -*- coding: utf-8 -*-

from pid import encontra_direcao_ate_cm, altera_velociade, altera_velociade_bater_creeper
from leitura_tags import encontra_tag_150
import math
from leitura_tags import * 

vel_ang = math.pi/15


def inicializou(temp_image, imagem_figuras_desenhadas, estado, velocidade):
    v_ang = velocidade.angular.z

    erro, sin_alfa = encontra_direcao_ate_cm(temp_image, "amarelo", imagem_figuras_desenhadas)
    if erro != None:
        velocidade = altera_velociade(velocidade, erro, sin_alfa)
        v_ang = velocidade.angular.z
    else:
        velocidade.linear.x = 0
        velocidade.angular.z = (v_ang)
        pass
    
    if encontra_tag_150(temp_image, imagem_figuras_desenhadas):
        estado = "rotate_until_is_creeper_visible"
        print("ROTACIONAR ATé ENCONTRAR CREEPER DA COR CErTA")

    return estado, velocidade


def rotate_to_find_creeper(temp_image, imagem_figuras_desenhadas, is_creeper_visible, estado, velocidade):

    velocidade.linear.x = 0
    velocidade.angular.z = -3*vel_ang

    if is_creeper_visible:
        menor_distancia_ate_creeper, corners, ids = identifica_tag(temp_image, imagem_figuras_desenhadas)
        if verifica_id_creeper(ids, menor_distancia_ate_creeper) == "identificou_o_creeper":
            estado = "seguir_creeper"
            print("SEGUIR o CREEPEr")

    return estado, velocidade


def go_to_creeper(temp_image, imagem_figuras_desenhadas, is_creeper_visible, estado, velocidade, cor_do_creeper):
    menor_distancia, corners, ids = identifica_tag(temp_image, imagem_figuras_desenhadas)

    erro, sin_alfa = encontra_direcao_ate_cm(temp_image, cor_do_creeper, imagem_figuras_desenhadas)
    if erro != None:
        velocidade = altera_velociade_bater_creeper(velocidade, erro, sin_alfa)

    if menor_distancia <= 230:
        estado = "voltar_pra_pista"
        print("VOLTAR PRA PISTA LOUCAMENTE")
    
    return estado, velocidade

def voltar_pra_pista(temp_image, imagem_figuras_desenhadas, estado, velocidade):
    distancia_cm_ao_centro, sin_alfa = encontra_direcao_ate_cm(temp_image, "amarelo", imagem_figuras_desenhadas)
    if distancia_cm_ao_centro == None:
        velocidade.linear.x  = -0.3
        velocidade.angular.z = 2*vel_ang
    else:
        estado = "terminar_circuito" #se enxergar a pista, volta a seguir
        print("TERMINAR CIRCUITO")

    return estado, velocidade

def finish_circuito(temp_image, imagem_figuras_desenhadas, estado, velocidade):
    erro, sin_alfa = encontra_direcao_ate_cm(temp_image, "amarelo", imagem_figuras_desenhadas)
    leitura_tag(temp_image, imagem_figuras_desenhadas, estado)

    if erro != None:
        velocidade = altera_velociade(velocidade, erro, sin_alfa)
    else:
        # velocidade.linear.x = 0
        velocidade.angular.z = 2*vel_ang
        pass

    return estado, velocidade

def leitura_tag(temp_image, imagem_figuras_desenhadas, estado):
    menor_distancia_id, corners, ids = identifica_tag(temp_image, imagem_figuras_desenhadas)
    if ids != None and menor_distancia_id <= 300:
        for i in ids:
            if str(i[0]) == "200":
                estado = "fazendo_a_curva"
    
    return estado

def fazer_curva(estado, velocidade):
    print("BORA FAZER A CURVA")
    velocidade.linear.x = 0

    return velocidade
    # velocidade.angular.z = 2*vel_ang