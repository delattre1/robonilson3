import cv2.aruco as aruco
import sys
import numpy as np 
import cv2

#--- Define Tag de teste
id_to_find  = 200
marker_size  = 25 #- [cm]
#id_to_find  = 22
#marker_size  = 3 #- [cm]
# 

#--- Get the camera calibration path
calib_path  = "/home/borg/catkin_ws/src/robot202/ros/exemplos202/scripts/"
camera_matrix   = np.loadtxt(calib_path+'cameraMatrix_raspi.txt', delimiter=',')
camera_distortion   = np.loadtxt(calib_path+'cameraDistortion_raspi.txt', delimiter=',')

#--- Define the aruco dictionary
aruco_dict  = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters  = aruco.DetectorParameters_create()
parameters.minDistanceToBorder = 0
parameters.adaptiveThreshWinSizeMax = 1000

id_fim_pista = [100,150,200]
lowest_dist = 1000

def arucando(bgr_img):#troca nome  #não esta identificando direito, fazer dar meia volta quando a distancia for pequena 
    gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids != None:
        ret = aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, camera_distortion)
        rvec, tvec = ret[0][0,0,:], ret[1][0,0,:]
        distance = np.linalg.norm(tvec)

        if distance < lowest_dist:
            menor_distancia_tag_fim = distance


        for i in ids:
            if i in id_fim_pista and menor_distancia_tag_fim <= 200:
                print("estado = meia volta")

