import auxiliar as aux
import cv2
import numpy as np
import sys
import math
from encontra_intersecao import slope, y_intercept, line_intersect

cap = cv2.VideoCapture('testevideo1.mp4')
sensitivity = 15
lower_white = np.array([0, 0, 255-sensitivity])
upper_white = np.array([255, sensitivity, 255])

min_line_length = 30
max_line_gap = 15
menor_m = 0
maior_m = 0
l_maior = [0]*4
l_menor = [0]*4

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # create a filter for white color
    mask = cv2.inRange(frame_hsv, lower_white, upper_white)

    src = mask  # frame
    # aplica o detector de bordas de Canny à imagem src
    dst = cv2.Canny(src, 200, 350)
    # Converte a imagem para BGR para permitir desenho colorido
    cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)

    # houghlinesp
    linesp = cv2.HoughLinesP(dst, 10, math.pi/180.0,
                             100, np.array([]), min_line_length, max_line_gap)
    a, b, c = linesp.shape
#   print(linesp)
    for i in range(a):
        l = linesp[i][0]
        m = (l[2] - l[0]) / (l[3] - l[1])
        if m > maior_m:
            maior_m = m
            l_maior = l
        elif m < menor_m:
            menor_m = m
            l_menor = l
        #print(f'coef ang :{m}')
        # cv2.waitKey(0)
        #cv2.line(cdst, (l[0], l[1]), (l[2], l[3]), (255, 0, 0), 3, cv2.LINE_AA)
    # print(f'menor: {menor_m} maior: {maior_m}')
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
    cv2.imshow("frame", cdst)
    # cv2.imshow("ajja",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
