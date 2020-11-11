#! /usr/bin/env python
# -*- coding:utf-8 -*-

import rospy

import numpy as np

import cv2

import math

from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan

laser = None

def scaneou(dado):
    print("Faixa valida: ", dado.range_min , " - ", dado.range_max )
    print("Leituras:")
    atual = np.array(dado.ranges).round(decimals=2)
    print(atual)
    global laser
    laser = atual.copy()
    #print("Intensities")
    #print(np.array(dado.intensities).round(decimals=2))


def desenha(cv_image):
    """
        Use esta funćão como exemplo de como desenhar na tela
    """
    #cv2.circle(cv_image,(256,256),64,(0,255,0),2)
    #cv2.line(cv_image,(256,256),(400,400),(255,0,0),5)
    #font = cv2.FONT_HERSHEY_SIMPLEX
    #cv2.putText(cv_image,'Boa sorte!',(0,50), font, 2,(255,255,255),2,cv2.LINE_AA)

    img = cv_image 

    if laser is not None:
        for  i in range(len(laser)):
            alpha = math.radians(i)
            cx, cy = (256, 256)
            d = laser[i]
            if 0.12  < d < 3.5:
                px = cx - d*math.sin(alpha)*50
                py = cy - d*math.cos(alpha)*50
                cv2.circle(img,(int(px),int(py)),2,(255,255,255),-1)
    
        hough_img = img[:,:,0]

        lines = cv2.HoughLinesP(hough_img, 10, math.pi/180.0, 100, np.array([]), 45, 5)

        if lines is not None: 
            a,b,c = lines.shape
            for i in range(a):
                # Faz uma linha ligando o ponto inicial ao ponto final, com a cor vermelha (BGR)
                cv2.line(img, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (0, 0, 255), 5, cv2.LINE_AA)


if __name__=="__main__":

    rospy.init_node("le_scan")

    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 3 )
    recebe_scan = rospy.Subscriber("/scan", LaserScan, scaneou)


    cv2.namedWindow("Saida")

    while not rospy.is_shutdown():
        print("Oeee")
        velocidade = Twist(Vector3(0, 0, 0), Vector3(0, 0, 0.5))
        velocidade_saida.publish(velocidade)
        # Cria uma imagem 512 x 512
        branco = np.zeros(shape=[512, 512, 3], dtype=np.uint8)
        # Chama funćões de desenho
        desenha(branco)

        # Imprime a imagem de saida
        cv2.imshow("Saida", branco)
        cv2.waitKey(1)
        rospy.sleep(0.1)