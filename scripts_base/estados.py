from pid import encontra_direcao_ate_cm, altera_velociade
from leitura_tags import encontra_tag_150
import math
from leitura_tags import * 

vel_ang = math.pi/15


def inicializou(temp_image, imagem_figuras_desenhadas, estado, velocidade):

    erro, sin_alfa = encontra_direcao_ate_cm(temp_image, "amarelo", imagem_figuras_desenhadas)
    if erro != None:
        velocidade = altera_velociade(velocidade, erro, sin_alfa)
    else:
        velocidade.linear.x = 0
        # velocidade.angular.z = -4*vel_ang
    
    if encontra_tag_150(temp_image, imagem_figuras_desenhadas):
        estado = "rotate_until_is_creeper_visible"
        print("estado na fun: {}").format(estado)

    return estado, velocidade


def rotate_to_find_creeper(temp_image, imagem_figuras_desenhadas, is_creeper_visible, estado, velocidade):

    velocidade.linear.x = 0
    velocidade.angular.z = -3*vel_ang

    if is_creeper_visible:
        menor_distancia_ate_creeper, corners, ids = identifica_tag(temp_image, imagem_figuras_desenhadas)
        if verifica_id_creeper(ids, menor_distancia_ate_creeper) == "identificou_o_creeper":
            estado = "seguir_creeper"

    return estado, velocidade

