#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2, rospy, time, tf2_ros, math

from sensor_msgs.msg   import Image, CompressedImage
from cv_bridge         import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped

from tf import transformations
from tf import TransformerROS

import encontra_centro_massa

def roda_todo_frame(imagem):
    global velocidade

    now = rospy.get_rostime()
    imgtime = imagem.header.stamp

    try:
        antes = time.clock()
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        cor_mascara = 'amarelo'

        which_direction_go = encontra_centro_massa.direcao_centro_massa_cor_escolhida(temp_image, cor_mascara)
        print(which_direction_go)

        velocidade = encontra_centro_massa.movimenta_to_centro_massa(which_direction_go, velocidade, vel_lin, vel_ang)

        cv2.imshow("temp img ", temp_image)       

        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)

bridge = CvBridge()

vel_lin = 0.25
vel_ang = math.pi/15
velocidade = Twist(Vector3(vel_lin,0,0), Vector3(0,0, 0))

tfl = 0
tf_buffer = tf2_ros.Buffer()


if __name__=="__main__":
    rospy.init_node("cor")  
    topico_imagem = "/camera/image/compressed"
    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)
    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)
    tfl = tf2_ros.TransformListener(tf_buffer) #conversao do sistema de coordenadas 

    try:
        while not rospy.is_shutdown():
            velocidade_saida.publish(velocidade)
            rospy.sleep(0.1)

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")