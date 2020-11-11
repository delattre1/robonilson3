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
                menor_distancia_tag_fim = distance   

            print('Distancia da tag: {}').format(distance)
        
        return menor_distancia_tag_fim, corners, ids
    except:
        return None,None,None
        

# def mover_ate_creeper(bgr_img, imagem_figuras_desenhadas, is_creeper_visible):
#     if is_creeper_visible:
#         try: 
#             distancia_ate_tag, corners, ids = identifica_tag(bgr_img, imagem_figuras_desenhadas)
#             #-- Desenha um retanculo e exibe Id do marker encontrado

#             aruco.drawDetectedMarkers(imagem_figuras_desenhadas, corners, ids) 
#             print(distancia_ate_tag)
#             for i in ids:
#                 if distancia_ate_tag <= 1500:
#                     print("estado = move to direction of creeper")
#                     # print("{}").format(i)

#         except:
#             pass    


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
id_fim_pista = [100,150,200]
marker_size  = 25 #- [cm]
id_to_find = 21
