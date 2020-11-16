#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2.aruco as aruco
import sys
import numpy as np 
import cv2

def identifica_tag(bgr_img, imagem_figuras_desenhadas):
    try: 
        gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        if ids is not None:
            aruco.drawDetectedMarkers(imagem_figuras_desenhadas, corners, ids) 

            ret = aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, camera_distortion)
            rvec, tvec = ret[0][0,0,:], ret[1][0,0,:]
            distance = np.linalg.norm(tvec)

            if distance < lowest_dist:
                menor_distancia = distance   

            print('Distancia da tag: {}').format(distance)
        
        return menor_distancia, corners, ids
    except:
        return 10000000,None,None


def encontra_tag_150(temp_image, imagem_figuras_desenhadas):
    menor_distancia, corners, ids = identifica_tag(temp_image, imagem_figuras_desenhadas)
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
        
#--- Get the camera calibration path
calib_path  = "/home/borg/catkin_ws/src/robot202/ros/exemplos202/scripts/"
camera_matrix   = np.loadtxt(calib_path+'cameraMatrix_raspi.txt', delimiter=',')
camera_distortion   = np.loadtxt(calib_path+'cameraDistortion_raspi.txt', delimiter=',')

#--- Define the aruco dictionary
aruco_dict  = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters  = aruco.DetectorParameters_create()
parameters.minDistanceToBorder = 0
parameters.adaptiveThreshWinSizeMax = 1000

lowest_dist = 1500
marker_size  = 25 #- [cm]
id_to_find = 21
lista_ids_fim_caminho = [50,100,150,200]
