#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2, rospy, time, tf2_ros, math

from sensor_msgs.msg   import Image, CompressedImage, LaserScan
from cv_bridge         import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped

from tf import transformations
from tf import TransformerROS

import encontra_centro_massa, leitura_tags
from encontra_centro_massa import direcao_centro_massa_cor_escolhida, restringir_window_creeper_e_tags

from pid import cria_linha_caminho, altera_velociade

def encontra_tag_150(temp_image, imagem_figuras_desenhadas):
    # list_xo_y0 = [60,60]
    # temp_image = restringir_window_creeper_e_tags(temp_image, list_xo_y0)
    menor_distancia, corners, ids = leitura_tags.identifica_tag(temp_image, imagem_figuras_desenhadas)
    if ids is not None:
        for numero_tag in ids:

            if numero_tag[0] == 150 and menor_distancia <= 450:
                return True
    return False

def verifica_id_creeper(ids, menor_distancia):
    if ids is not None:
        for numero_tag in ids:
            if numero_tag[0] not in lista_ids_fim_caminho:
                if menor_distancia <= 2200 and (menor_distancia is not None):
                    return "identificou_o_creeper"


def roda_todo_frame(imagem):
    global velocidade
    global estado

    now = rospy.get_rostime()
    imgtime = imagem.header.stamp

    try:
        antes = time.clock()
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")


        imagem_figuras_desenhadas = temp_image.copy()
        # is_creeper_visible, posicao_centro_massa_creeper = encontra_centro_massa.buscar_creeper(temp_image, cor_do_creeper_buscar, imagem_figuras_desenhadas)


        erro, tg = cria_linha_caminho(temp_image, "amarelo", imagem_figuras_desenhadas)
        if erro != None:
            velocidade = altera_velociade(velocidade, erro, tg)
            # print(velocidade)

        # if estado == "inicializou":

        #     if encontra_tag_150(temp_image, imagem_figuras_desenhadas) == True:
        #         estado = "rotate_until_is_creeper_visible"

        #     which_direction_go = direcao_centro_massa_cor_escolhida(temp_image, cor_mascara_pista, imagem_figuras_desenhadas)



        # elif estado == "seguir_creeper":
        #     menor_distancia, corners, ids = leitura_tags.identifica_tag(temp_image, imagem_figuras_desenhadas)

        #     which_direction_go = encontra_centro_massa.move_to_creeper(posicao_centro_massa_creeper)

        #     if menor_distancia <= 240:
        #         estado = "terminar_circuito"


        # elif estado == 'terminar_circuito':
        #     which_direction_go = direcao_centro_massa_cor_escolhida(temp_image, cor_mascara_pista, imagem_figuras_desenhadas)
        #     distancia_tag_fazer_curva, corners, ids = leitura_tags.identifica_tag(temp_image, imagem_figuras_desenhadas)
        #     if ids is not None:
        #         for i in ids:
        #             if i[0] == 200:
        #                 print("identifiquei a tag que é pra virar pra esquerda")
        

        # elif estado == "rotate_until_is_creeper_visible":
        #     which_direction_go = 'rotate_until_is_creeper_visible'
        #     if is_creeper_visible:
        #         menor_distancia_ate_creeper, corners, ids = leitura_tags.identifica_tag(temp_image, imagem_figuras_desenhadas)
        #         if verifica_id_creeper(ids, menor_distancia_ate_creeper) == "identificou_o_creeper":
        #             estado = "seguir_creeper"

        # velocidade = encontra_centro_massa.movimenta_to_centro_massa(which_direction_go, velocidade, vel_lin, vel_ang)

        cv2.imshow("temp img ", imagem_figuras_desenhadas)       
        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)

bridge = CvBridge()

vel_lin = 0.25
vel_ang = math.pi/15
velocidade = Twist(Vector3(vel_lin,0,0), Vector3(0,0, 0))

tfl = 0
tf_buffer = tf2_ros.Buffer()

cor_do_creeper_buscar = "pink"  #pink blue vermelho
cor_mascara_pista     = 'amarelo'        


estado = "inicializou"

lista_ids_fim_caminho = [50,100,150,200]

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