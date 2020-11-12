#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2, rospy, time, tf2_ros, math

from sensor_msgs.msg   import Image, CompressedImage, LaserScan
from cv_bridge         import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped

from tf import transformations
from tf import TransformerROS

import encontra_centro_massa, leitura_tags
from encontra_centro_massa import direcao_centro_massa_cor_escolhida, restringir_window_creeper_e_tags, buscar_creeper
from leitura_tags import encontra_tag_150, verifica_id_creeper
from pid import encontra_direcao_ate_cm, altera_velociade, altera_velociade_bater_creeper

from estados import *


def go_to_creeper(temp_image, imagem_figuras_desenhadas):
    global velocidade
    global estado
    global contador_bateu_creeper

    menor_distancia, corners, ids = leitura_tags.identifica_tag(temp_image, imagem_figuras_desenhadas)

    erro, sin_alfa = encontra_direcao_ate_cm(temp_image, cor_do_creeper_buscar, imagem_figuras_desenhadas)
    if erro != None:
        velocidade = altera_velociade_bater_creeper(velocidade, erro, sin_alfa)

    if menor_distancia <= 240:
        contador_bateu_creeper += 1
        if contador_bateu_creeper >= 5:
            estado = "voltar_pra_pista"



def voltar_pra_pista(temp_image, imagem_figuras_desenhadas):
    global velocidade
    global estado

    distancia_cm_ao_centro, sin_alfa = encontra_direcao_ate_cm(temp_image, "amarelo", imagem_figuras_desenhadas)
    if distancia_cm_ao_centro == None:
        velocidade.linear.x  = -0.3
        velocidade.angular.z = 2*vel_ang
    else:
        estado = "terminar_circuito"



def finish_circuito(temp_image, imagem_figuras_desenhadas):
    global velocidade
    global estado

    erro, sin_alfa = encontra_direcao_ate_cm(temp_image, "amarelo", imagem_figuras_desenhadas)
    if erro != None:
        velocidade = altera_velociade(velocidade, erro, sin_alfa)
    else:
        velocidade.linear.x = 0
        velocidade.angular.z = -4*vel_ang

        
def roda_todo_frame(imagem):
    global velocidade
    global estado

    now     = rospy.get_rostime()
    imgtime = imagem.header.stamp

    #não está enxergando a pista
    try:
        print("estado no codigo: {}").format(estado)

        antes = time.clock()
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        imagem_figuras_desenhadas = temp_image.copy()

        is_creeper_visible, posicao_centro_massa_creeper = buscar_creeper(temp_image, cor_do_creeper_buscar, imagem_figuras_desenhadas)

        if   estado == "inicializou":
            estado, velocidade = inicializou(temp_image, imagem_figuras_desenhadas, estado, velocidade)

        elif estado == "rotate_until_is_creeper_visible":
            estado, velocidade = rotate_to_find_creeper(temp_image, imagem_figuras_desenhadas, is_creeper_visible, estado, velocidade)
        
        elif estado == "seguir_creeper":
            go_to_creeper(temp_image, imagem_figuras_desenhadas)

        elif estado == "voltar_pra_pista":
            voltar_pra_pista(temp_image, imagem_figuras_desenhadas)
            

        elif estado == 'terminar_circuito':
            finish_circuito(temp_image, imagem_figuras_desenhadas)


        cv2.imshow("temp img ", imagem_figuras_desenhadas)       
        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)

bridge = CvBridge()

vel_lin = 0.0
vel_ang = math.pi/15
velocidade = Twist(Vector3(vel_lin,0,0), Vector3(0,0, 0))

tfl = 0
tf_buffer = tf2_ros.Buffer()

cor_do_creeper_buscar = "pink"  #pink blue vermelho
cor_mascara_pista     = 'amarelo'        

estado = "inicializou"
contador_bateu_creeper = 0



if __name__=="__main__":
    rospy.init_node("cor")  
    topico_imagem = "/camera/image/compressed"
    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)
    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)

    tfl = tf2_ros.TransformListener(tf_buffer) #conversao do sistema de coordenadas 

    try:
        while not rospy.is_shutdown():
            velocidade_saida.publish(velocidade)
            rospy.sleep(0.05)

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")