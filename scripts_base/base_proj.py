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

#variaveis e import relacionados a plota frame_hsv
from encontra_intersecao import slope, y_intercept, line_intersect
sensitivity = 15
lower_white = np.array([0, 0, 255-sensitivity])
upper_white = np.array([255, sensitivity, 255])
min_line_length = 30
max_line_gap = 15
menor_m = 0
maior_m = 0
l_maior = [0]*4
l_menor = [0]*4

def plota_frame_hsv(frame):
    maior_m, menor_m = 0, 0

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame_hsv, lower_white, upper_white)
    # aplica o detector de bordas de Canny à imagem src
    dst = cv2.Canny(mask, 200, 350)
    # Converte a imagem para BGR para permitir desenho colorido
    cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    # houghlinesp
    linesp = cv2.HoughLinesP(dst, 10, math.pi/180.0,
                             100, np.array([]), min_line_length, max_line_gap)

    a, b, c = linesp.shape
    for i in range(a):
        l = linesp[i][0]
        m = (l[2] - l[0]) / (l[3] - l[1])
        if m > maior_m:
            maior_m = m
            l_maior = l
        elif m < menor_m:
            menor_m = m
            l_menor = l

    cv2.line(cdst, (l_maior[0], l_maior[1]), (l_maior[2],
                                              l_maior[3]), (255, 0, 255), 3, cv2.LINE_AA)

    cv2.line(cdst, (l_menor[0], l_menor[1]), (l_menor[2],
                                              l_menor[3]), (25, 240, 255), 3, cv2.LINE_AA)

    p1, p2 = (l_maior[0],l_maior[1]),(l_maior[2],l_maior[3])
    q1, q2 = (l_menor[0],l_menor[1]),(l_menor[2],l_menor[3])
    m1 = slope(p1,p2)
    m2 = slope(q1,q2)
    yint_a = y_intercept(p1, m1)
    yint_b = y_intercept(q1,m2)
    ponto_de_fuga =  (line_intersect(m1, yint_a, m2, yint_b))
    x_fuga = int(ponto_de_fuga[0])
    y_fuga = int(ponto_de_fuga[1])
    cv2.circle(cdst, (x_fuga,y_fuga), 2, (0,0,255), 10)
    maior_m, menor_m = 0, 0
    # display
    cv2.imshow("nome frame tela", cdst)

    return None

# A função a seguir é chamada sempre que chega um novo frame
def roda_todo_frame(imagem):
    print("frame")
    global cv_image
    global media
    global centro
    global resultados

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

        # Note que os resultados já são guardados automaticamente na variável
        # chamada resultados
        centro, saida_net, resultados =  visao_module.processa(temp_image)        
        for r in resultados:
            # print(r) - print feito para documentar e entender
            # o resultado            
            pass

        depois = time.clock()
        # Desnecessário - Hough e MobileNet já abrem janelas
        cv_image = saida_net.copy()


        plota_frame_hsv(temp_image)


        # cv2.imshow("cv_image", cv_image)
        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)
    
if __name__=="__main__":
    rospy.init_node("cor")

    topico_imagem = "/camera/image/compressed"

    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)


    print("Usando ", topico_imagem)

    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)

    tfl = tf2_ros.TransformListener(tf_buffer) #conversao do sistema de coordenadas 
    tolerancia = 25

    # Exemplo de categoria de resultados
    # [('chair', 86.965459585189819, (90, 141), (177, 265))]

    try:
        # Inicializando - por default gira no sentido anti-horário
        # vel = Twist(Vector3(0,0,0), Vector3(0,0,math.pi/10.0))
        
        while not rospy.is_shutdown():
            for r in resultados:
                print(r)
            #velocidade_saida.publish(vel)

            rospy.sleep(0.1)

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")


