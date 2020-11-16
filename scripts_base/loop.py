#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2, rospy, time, tf2_ros, math

from sensor_msgs.msg   import Image, CompressedImage, LaserScan
from cv_bridge         import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped

from tf import transformations, TransformerROS
from move_garra import garra
from pid2 import encontra_direcao_ate_cm, altera_velociade, is_creeper_visible
from tags_id import should_rotacionar_to_find_creeper, distance_creeper

from movimentacao import *

bridge = CvBridge()
vel_lin = 0.0
vel_ang = math.pi/15

velocidade = Twist(Vector3(vel_lin,0,0), Vector3(0,0, vel_ang))
tfl = 0
tf_buffer = tf2_ros.Buffer()

cor_do_creeper = "pink"    #pink blue vermelho - (ORANGE É o VERMELhO)
creeper_id     = 13        #blue 22 , "pink 13", orange 11

cor_mascara_pista  = 'amarelo'        
estado             = "ajustar posicao inicial"  #Teste da garra
garra = garra()

tempo_rotacao_inicio = 0.1
time_rodar_after_pegar_creeper = 0.1

def roda_todo_frame(imagem):
    global estado
    global velocidade 
    global tempo_rotacao_inicio
    global time_rodar_after_pegar_creeper

    try:
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        imagem_figuras_desenhadas = temp_image.copy()

        if estado == "ajustar posicao inicial":
            if cor_do_creeper == "blue" or cor_do_creeper == "vermelho":
                estado, velocidade, tempo_rotacao_inicio = rotacionar_no_inicio(estado, velocidade, cor_do_creeper)

            elif cor_do_creeper == "pink":
                estado = "resetar garra"

        if estado == "inicializou":
            estado, velocidade = anda_rapidamente_pista(estado, velocidade, temp_image, cor_mascara_pista, imagem_figuras_desenhadas)
            estado = deve_dar_meia_volta(estado, temp_image, imagem_figuras_desenhadas)
            # print("ESTADO: {}").format(estado)

        elif estado == "dar meia volta":
            estado, velocidade = rodar_until_creeper_located(estado, velocidade, temp_image, imagem_figuras_desenhadas, cor_do_creeper)
            print("ESTADO: {}").format(estado)

        elif estado == "go_to_creeper":
            #roda Função que faz robô ir até o creeper e depois parar
            erro_x, tg_alfa = is_creeper_visible(temp_image, cor_do_creeper, imagem_figuras_desenhadas)
            velocidade = altera_velociade(velocidade, erro_x, tg_alfa, estado)
            print("ESTADO: {}").format(estado)
            if distance_creeper(temp_image, imagem_figuras_desenhadas, creeper_id):
                estado = "parar em frente ao creeper"

        elif estado == "parar em frente ao creeper":
            print("ESTADO: {}").format(estado)
            estado, velocidade = parar_frente_creeper(estado, velocidade)

        elif estado == "capturar creeper":
            print("ESTADO: {}").format(estado)
            estado, velocidade = captura_creeper(estado, velocidade, garra)

        elif estado == "endireitar":
            print("ESTADO: {}").format(estado)
            estado, velocidade, time_rodar_after_pegar_creeper = endireitar_depois_de_pegar_creeper(estado, velocidade, cor_do_creeper)

        elif estado == "voltar pra pista":
            print("ESTADO: {}").format(estado)
            estado, velocidade = anda_rapidamente_pista(estado, velocidade, temp_image, cor_mascara_pista, imagem_figuras_desenhadas)

        cv2.imshow("temp img", imagem_figuras_desenhadas)       

        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)

def captura_creeper(estado, velocidade, garra):
    print("capturando o creeper")
    garra.publish_bobo()
    rospy.sleep(.1)

    garra.abre_garra()
    rospy.sleep(.1)

    garra.ergue_garra()
    rospy.sleep(.5)

    garra.fecha_garra()
    rospy.sleep(.5)

    garra.ergue_garra()
    rospy.sleep(.5)

    velocidade.angular.z = -2*vel_ang

    estado = "endireitar"
    return estado, velocidade

def publish_velocidade(publisher, velocidade, estado):
    publisher.publish(velocidade)
    rospy.sleep(.1)

    if estado == "ajustar posicao inicial":
        publisher.publish(velocidade)
        rospy.sleep(tempo_rotacao_inicio)
        #Para parar o movimento
        velocidade.angular.z = 0
        publisher.publish(velocidade)
        rospy.sleep(.05)

    elif estado == "endireitar":
        publisher.publish(velocidade)
        rospy.sleep(time_rodar_after_pegar_creeper)

    else:
        rospy.sleep(.05)

if __name__=="__main__":
    rospy.init_node("cor")  
    topico_imagem = "/camera/image/compressed"
    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)
    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)

    tfl = tf2_ros.TransformListener(tf_buffer) #Conversão do sistema de coordenadas 

    try:
        while not rospy.is_shutdown():
            if estado == "ajustar posicao inicial":
                publish_velocidade(velocidade_saida, velocidade,estado)
                print("estou ajustando posicao inicial")
                estado = "resetar garra"

            elif estado == "endireitar":
                publish_velocidade(velocidade_saida, velocidade,estado)
                print("endireitando em direção a pista")
                estado = "voltar pra pista"

            else:
                publish_velocidade(velocidade_saida, velocidade, estado)

            if estado == "resetar garra":
                garra.fecha_garra()
                rospy.sleep(.5)
                garra.publish_bobo()
                rospy.sleep(.5)  
                estado = "inicializou"

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")

