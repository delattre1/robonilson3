#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import numpy as np 

# print("Baixe o arquivo a seguir para funcionar: ")
# print("https://github.com/Insper/robot202/raw/master/projeto/centro_massa/line_following.mp4")

# cap = cv2.VideoCapture('line_following.mp4')

# Valores para amarelo usando um color picker
low = np.array([22, 50, 50],dtype=np.uint8)
high = np.array([36, 255, 255],dtype=np.uint8)

def filter_color(bgr, low, high):
    """ REturns a mask within the range"""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    return mask     

# Função centro de massa baseada na aula 02  https://github.com/Insper/robot202/blob/master/aula02/aula02_Exemplos_Adicionais.ipynb
# Esta função calcula centro de massa de máscara binária 0-255 também, não só de contorno
def center_of_mass(mask):
    """ Retorna uma tupla (cx, cy) que desenha o centro do contorno"""
    M = cv2.moments(mask)
    # Usando a expressão do centróide definida em: https://en.wikipedia.org/wiki/Image_moment
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return [int(cX), int(cY)]

def crosshair(img, point, size, color):
    """ Desenha um crosshair centrado no point.
        point deve ser uma tupla (x,y)
        color é uma tupla R,G,B uint8
    """
    x,y = point
    cv2.line(img,(x - size,y),(x + size,y),color,5)
    cv2.line(img,(x,y - size),(x, y + size),color,5)

def center_of_mass_region(mask, x1, y1, x2, y2):
    # Para fins de desenho
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    clipped = mask[y1:y2, x1:x2]
    c = center_of_mass(clipped)
    c[0]+=x1
    c[1]+=y1
    crosshair(mask_bgr, c, 10, (0,0,255))
    cv2.rectangle(mask_bgr, (x1, y1), (x2, y2), (255,0,0),2,cv2.LINE_AA)
    return mask_bgr

def seleciona_window_centro_de_massa(img_bgr):
    low_yellow, high_yellow = np.array([22, 50, 50],dtype=np.uint8), np.array([36, 255, 255],dtype=np.uint8)
    yellow_mask = filter_color(img_bgr, low_yellow, high_yellow)
    #selecionar window
    x0 = 0
    y0 = 40
    x1 = img_bgr.shape[1]
    print('é a metade: []{}'.format(x1/2))
    y1 = img_bgr.shape[0] - y0
    clipped = yellow_mask[y0:y1, x0:x1]
    try: 
        c = center_of_mass(clipped) 
        desenha_centro = crosshair(img_bgr, c, 20, (255,0,255))
        cv2.rectangle(img_bgr, (x0, y0), (x1, y1), (255,0,0),2,cv2.LINE_AA) #desenha retangulo da área selecionada
        print(c)
        print("")

        rotacao_conforme_centro_pista(c)
    except:
        print('falha ao selecionar estrada')
    return img_bgr

def rotacao_conforme_centro_pista(centro_massa):
    x_centro = centro_massa[0]
    incerteza = 10
    centro = 160
    if x_centro < centro - incerteza: #meio é 160
        print("tem que girar pra esquerda (+vel_ang)")
    elif x_centro > centro + incerteza:
        print("tem que virar pra direita (-vel ang) ")
    
    return None

# while(True):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
    
#     if ret == False:
#         print("Codigo de retorno FALSO - problema para capturar o frame")

#     # Our operations on the frame come here
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    
#     cv2.imshow('frame',frame)
#     mask = filter_color(frame, low, high)
#     mask_bgr = center_of_mass_region(mask, 20, 200, frame.shape[1] - 20, frame.shape[0]-100) # Lembrando que negativos contam a partir do fim`
#     cv2.imshow('mask', mask_bgr)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()






# #variaveis e import relacionados a plota frame_hsv
# from encontra_intersecao import slope, y_intercept, line_intersect
# sensitivity = 15
# lower_white = np.array([0, 0, 255-sensitivity])
# upper_white = np.array([255, sensitivity, 255])
# min_line_length = 45
# max_line_gap = 18
# menor_m = 0
# maior_m = 0
# l_maior = [0]*4
# l_menor = [0]*4


# def plota_frame_hsv(frame):
#     #funcao que seleciona apenas a pista em branco, consigo selecionar a cor bonitinho, porem a interseção não está working 
#     maior_m, menor_m = 0, 0
#     frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     mask = cv2.inRange(frame_hsv, lower_white, upper_white)
#     # aplica o detector de bordas de Canny à imagem src
#     dst = cv2.Canny(mask, 200, 350)
#     try:
#         # Converte a imagem para BGR para permitir desenho colorido
#         cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
#         # houghlinesp
#         linesp = cv2.HoughLinesP(dst, 10, math.pi/180.0,
#                                 100, np.array([]), min_line_length, max_line_gap)

#         print(linesp)
#         a, b, c = linesp.shape
#         for i in range(a):
#             l = linesp[i][0]
#             m = (l[2] - l[0]) / (l[3] - l[1])
#             if m > maior_m:
#                 maior_m = m
#                 l_maior = l
#             elif m < menor_m:
#                 menor_m = m
#                 l_menor = l

#         cv2.line(cdst, (l_maior[0], l_maior[1]), (l_maior[2],
#                                                 l_maior[3]), (255, 0, 255), 3, cv2.LINE_AA)

#         cv2.line(cdst, (l_menor[0], l_menor[1]), (l_menor[2],
#                                                 l_menor[3]), (25, 240, 255), 3, cv2.LINE_AA)
        
#         # p1, p2 = (l_maior[0],l_maior[1]),(l_maior[2],l_maior[3])
#         # q1, q2 = (l_menor[0],l_menor[1]),(l_menor[2],l_menor[3])
#         # m1 = slope(p1,p2)
#         # m2 = slope(q1,q2)
#         # yint_a = y_intercept(p1, m1)
#         # yint_b = y_intercept(q1,m2)
#         # ponto_de_fuga =  (line_intersect(m1, yint_a, m2, yint_b))
#         # x_fuga = int(ponto_de_fuga[0])
#         # y_fuga = int(ponto_de_fuga[1])
#         # cv2.circle(cdst, (x_fuga,y_fuga), 2, (0,0,255), 10)
#         # maior_m, menor_m = 0, 0

#     except: 
#         print("erro na mask da pista")

#     cv2.imshow("nome frame tela", cdst)

#     return None