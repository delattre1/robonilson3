#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2, rospy, time, tf2_ros, math

from sensor_msgs.msg   import Image, CompressedImage, LaserScan
from cv_bridge         import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped

from tf import transformations
from tf import TransformerROS

bridge = CvBridge()
vel_lin = 0.0
vel_ang = math.pi/15

velocidade = Twist(Vector3(vel_lin,0,0), Vector3(0,0, vel_ang))
tfl = 0
tf_buffer = tf2_ros.Buffer()

cor_do_creeper     = "blue"    #pink blue vermelho
cor_mascara_pista  = 'amarelo'        
estado             = "inicializou" 

from pid2 import encontra_direcao_ate_cm, altera_velociade

def anda_rapidamente_pista(estado, velocidade, img_bgr_limpa, str_cor, img_bgr_visivel):
    erro_x, tg_alfa = encontra_direcao_ate_cm(img_bgr_limpa, str_cor, img_bgr_visivel)
    velocidade = altera_velociade(velocidade, erro_x, tg_alfa)
    return velocidade

def roda_todo_frame(imagem):
    global estado
    global velocidade 

    try:
        antes = time.clock()
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        imagem_figuras_desenhadas = temp_image.copy()

        if estado == "inicializou":
            velocidade = anda_rapidamente_pista(estado, velocidade, temp_image, cor_mascara_pista, imagem_figuras_desenhadas)

        cv2.imshow("temp img", imagem_figuras_desenhadas)       

        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)


if __name__=="__main__":
    rospy.init_node("cor")  
    topico_imagem = "/camera/image/compressed"
    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)
    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)

    tfl = tf2_ros.TransformListener(tf_buffer) #conversao do sistema de coordenadas 

    try:
        while not rospy.is_shutdown():
            velocidade_saida.publish(velocidade)
            rospy.sleep(0.01)

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")