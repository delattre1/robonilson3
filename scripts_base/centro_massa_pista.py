#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2, rospy, time, tf2_ros 

from sensor_msgs.msg   import Image, CompressedImage
from cv_bridge         import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped

from tf import transformations
from tf import TransformerROS


def roda_todo_frame(imagem):

    now = rospy.get_rostime()
    imgtime = imagem.header.stamp

    try:
        antes = time.clock()
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        cv2.imshow("temp img ", temp_image)

        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)

bridge = CvBridge()

vel_lin = 0.25
vel = Twist(Vector3(vel_lin,0,0), Vector3(0,0, 0))

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
            velocidade_saida.publish(vel)
            rospy.sleep(0.1)

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")