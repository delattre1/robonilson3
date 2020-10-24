#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function, division
import rospy
import numpy as np
import numpy
import tf
import math
import cv2
import time
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge, CvBridgeError
from numpy import linalg
from tf import transformations
from tf import TransformerROS
import tf2_ros
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped

from nav_msgs.msg import Odometry
from std_msgs.msg import Header
import visao_module


#usar mask para chão amarelo
import center_mass

bridge = CvBridge()

cv_image = None
media = []
centro = []
atraso = 1.5E9 # 1 segundo e meio. Em nanossegundos
area = 0.0 # Variavel com a area do maior contorno

# Só usar se os relógios ROS da Raspberry e do Linux desktop estiverem sincronizados. 
# Descarta imagens que chegam atrasadas demais
check_delay = False 

resultados = [] # Criacao de uma variavel global para guardar os resultados vistos
x = 0
y = 0
z = 0 
id = 0

frame = "camera_link"
# frame = "head_camera"  # DESCOMENTE para usar com webcam USB via roslaunch tag_tracking usbcam
tfl = 0
tf_buffer = tf2_ros.Buffer()

# def posicao_odometry(msg):
#     # print(msg.pose.pose)
#     x = msg.pose.pose.position.x
#     y = msg.pose.pose.position.y

#     quat = msg.pose.pose.orientation
#     lista = [quat.x, quat.y, quat.z, quat.w]
#     angulos_rad = transformations.euler_from_quaternion(lista)
#     alfa = angulos_rad[2]
#     angs_degree = np.degrees(angulos_rad)
#     print("Posicao (x,y)  ({:.2f} , {:.2f}) + angulo {:.2f}".format(x, y, angs_degree[2]))


vel = Twist(Vector3(0,0,0), Vector3(0,0, 0))

# A função a seguir é chamada sempre que chega um novo frame
def roda_todo_frame(imagem):
    print("frame")
    global cv_image
    global media
    global centro
    global resultados
    global vel

    vel_lin = 0.1 #velocidade linear
    now = rospy.get_rostime()
    imgtime = imagem.header.stamp
    lag = now-imgtime # calcula o lag
    delay = lag.nsecs
    # print("delay ", "{:.3f}".format(delay/1.0E9))
    if delay > atraso and check_delay==True:
        print("Descartando por causa do delay do frame:", delay)
        return 
    try:
        antes = time.clock()
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        window_selecionada, centro_de_massa = center_mass.seleciona_window_centro_de_massa(temp_image)
        cv2.imshow("Centro de massa com area selecionada", window_selecionada)

        go_in_which_direction = center_mass.rotacao_conforme_centro_pista(centro_de_massa)
        if go_in_which_direction == "virar esquerda":
            vel = Twist(Vector3(vel_lin,0,0), Vector3(0,0, math.pi/15))
        elif go_in_which_direction == "virar direita":
            vel = Twist(Vector3(vel_lin,0,0), Vector3(0,0, -math.pi/15))
        else:
            vel =  Twist(Vector3(2*vel_lin,0,0), Vector3(0,0, 0))



        # # Note que os resultados já são guardados automaticamente na variável
        # # chamada resultados
        # centro, saida_net, resultados =  visao_module.processa(temp_image)        
        # for r in resultados:
        #     # print(r) - print feito para documentar e entender
        #     # o resultado            
        #     pass

        # depois = time.clock()
        # # Desnecessário - Hough e MobileNet já abrem janelas
        # cv_image = saida_net.copy()
        # cv2.imshow("cv_image", cv_image)


        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)
    
if __name__=="__main__":
    rospy.init_node("cor")
    topico_imagem = "/camera/image/compressed"
    # odom_sub = rospy.Subscriber("/odom", Odometry, posicao_odometry)
    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)
    # print("Usando ", topico_imagem)
    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)
    tfl = tf2_ros.TransformListener(tf_buffer) #conversao do sistema de coordenadas 
    tolerancia = 25

    # Exemplo de categoria de resultados
    # [('chair', 86.965459585189819, (90, 141), (177, 265))]

    try:
        # Inicializando - por default gira no sentido anti-horário
        # vel = Twist(Vector3(0,0,0), Vector3(0,0, math.pi/10.0))
        while not rospy.is_shutdown():
            # for r in resultados:
            #     print(r)
            velocidade_saida.publish(vel)
            rospy.sleep(0.1)

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")

