#! /usr/bin/env python
# -*- coding:utf-8 -*-

import rospy, cv2, math
import numpy as np
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan

laser = None

def scaneou(dado):
    # print("Faixa valida: ", dado.range_min , " - ", dado.range_max )
    print("Leituras:")
    atual = np.array(dado.ranges).round(decimals=2)
    print(atual)
    print('')
    global laser
    laser = atual.copy()

    
