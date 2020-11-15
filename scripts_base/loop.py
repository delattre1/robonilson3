#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2, rospy, time, tf2_ros, math

from sensor_msgs.msg   import Image, CompressedImage, LaserScan
from cv_bridge         import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped

from tf import transformations
from tf import TransformerROS

from move_garra import claw

from pid2 import encontra_direcao_ate_cm, altera_velociade, is_creeper_visible
from tags_id import should_rotacionar_to_find_creeper, distance_creeper


bridge = CvBridge()
vel_lin = 0.0
vel_ang = math.pi/15

velocidade = Twist(Vector3(vel_lin,0,0), Vector3(0,0, vel_ang))
tfl = 0
tf_buffer = tf2_ros.Buffer()

cor_do_creeper = "blue"    #pink blue vermelho
creeper_id     = 22        #blue , "pink 13", orange 11

cor_mascara_pista  = 'amarelo'        
estado             = "resetar garra"  #'testegarra' 
claw = claw()

def anda_rapidamente_pista(estado, velocidade, img_bgr_limpa, str_cor, img_bgr_visivel):
    erro_x, tg_alfa = encontra_direcao_ate_cm(img_bgr_limpa, str_cor, img_bgr_visivel)
    velocidade = altera_velociade(velocidade, erro_x, tg_alfa, estado)
    return estado, velocidade

def deve_dar_meia_volta(estado, temp_image, imagem_figuras_desenhadas):
    if  should_rotacionar_to_find_creeper(temp_image, imagem_figuras_desenhadas):
        estado = "dar meia volta"
    return estado

def rodar_until_creeper_located(estado, velocidade, temp_image, imagem_figuras_desenhadas):
    velocidade.linear.x = 0
    velocidade.angular.z = -2*vel_ang

    if is_creeper_visible(temp_image, cor_do_creeper, imagem_figuras_desenhadas)[0] != None:
        estado = "go_to_creeper"
        velocidade.linear.x = 0
        velocidade.angular.z = 0
    return estado, velocidade

def roda_todo_frame(imagem):
    global estado
    global velocidade 
    # global contador_meia_volta

    try:
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        imagem_figuras_desenhadas = temp_image.copy()

        if estado == "inicializou":
            estado, velocidade = anda_rapidamente_pista(estado, velocidade, temp_image, cor_mascara_pista, imagem_figuras_desenhadas)
            estado = deve_dar_meia_volta(estado, temp_image, imagem_figuras_desenhadas)
            print("ESTADO: {}").format(estado)

            # contador_meia_volta = 0 

        elif estado == "dar meia volta": #and contador_meia_volta == 0:
            # contador_meia_volta = 1 #aqui deve rodar até o creeper estar visivel 
            estado, velocidade = rodar_until_creeper_located(estado, velocidade, temp_image, imagem_figuras_desenhadas)
            print("ESTADO: {}").format(estado)

        elif estado == "go_to_creeper":
            #roda func que faz robo ir até o creeper e parar
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
            estado, velocidade = captura_creeper(estado, velocidade)


        elif estado == "voltar pra pista":
            estado, velocidade = anda_rapidamente_pista(estado, velocidade, temp_image, cor_mascara_pista, imagem_figuras_desenhadas)

        cv2.imshow("temp img", imagem_figuras_desenhadas)       

        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)

def parar_frente_creeper(estado, velocidade):
    vx = velocidade.linear.x 
    if vx > 0:
        velocidade.linear.x -= 0.01
    else:
        velocidade.linear.x = 0.01
        estado = "capturar creeper"

    velocidade.angular.z = 0

    return estado, velocidade

def publish_velocidade(publisher, velocidade):
    publisher.publish(velocidade)
    rospy.sleep(0.01)

def captura_creeper(estado, velocidade):
    print("capturando o creeper")
    claw.publish_bobo()
    rospy.sleep(.1)

    claw.abre_garra()
    rospy.sleep(.1)

    claw.ergue_garra()
    rospy.sleep(.5)

    #dar uma aproximada para pegar

    claw.fecha_garra()
    rospy.sleep(.5)

    claw.ergue_garra()
    rospy.sleep(.5)

    velocidade.angular.z = -2*vel_ang

    estado = "voltar pra pista"
    print("É PRA VOLTAR PELA FUNCAO JÁ ")
    return estado, velocidade

# claw.down_arm()

if __name__=="__main__":
    rospy.init_node("cor")  
    topico_imagem = "/camera/image/compressed"
    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)
    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)

    tfl = tf2_ros.TransformListener(tf_buffer) #conversao do sistema de coordenadas 

    try:
        while not rospy.is_shutdown():
            # if estado == "dar meia volta" and contador_meia_volta == 1:
            #     velocidade.linear.x = 0
            #     velocidade.angular.z = 2.5*vel_ang
            #     velocidade_saida.publish(velocidade)
            #     tempo_sleep_meia_volta = math.pi/(2.5*vel_ang)
            #     rospy.sleep(tempo_sleep_meia_volta)
            #     contador_meia_volta = 2
            #     estado = "inicializou"

            # else:
            publish_velocidade(velocidade_saida, velocidade)

            if estado == "resetar garra":
                claw.fecha_garra()
                rospy.sleep(.5)
                claw.publish_bobo()
                rospy.sleep(.5)  

                estado = "inicializou"

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")

# def soltar_creeper():
    # claw.abaixa_garra()
    # rospy.sleep(1)

    # claw.abre_garra()
    # rospy.sleep(1)

    # claw.abaixa_garra()
    # rospy.sleep(1)

    # claw.fecha_garra()
    # rospy.sleep(1)