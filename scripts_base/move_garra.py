#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy, time
from std_msgs.msg import Float64

class garra:
    def __init__(self):
        self.arm_publisher = rospy.Publisher(
            '/joint1_position_controller/command',
            Float64,
            queue_size=1)
        self.garra_publisher = rospy.Publisher(
            '/joint2_position_controller/command',
            Float64,
            queue_size=1)

        self.arm_state  = -1
        self.garra_state =  0
        self.time = .1

    def publish_bobo(self):
        self.arm_state  = -1
        self.garra_state =  0
        
        print("abaixando garra...")
        self.arm_publisher.publish(self.arm_state)
        rospy.sleep(.1)

        print("fechando garra...")
        self.garra_publisher.publish(self.garra_state)
        rospy.sleep(.1)

    def ergue_garra(self):
        print("erguendo garra...")
        if self.arm_state == -1:
            self.arm_state = 0
        elif self.arm_state == 0:
            self.arm_state = 1.5
        
        self.arm_publisher.publish(self.arm_state)
        time.sleep(self.time)

    def abaixa_garra(self):
        print("abaixando garra...")
        if self.arm_state == 1.5:
            self.arm_state = 0
        elif self.arm_state == 0:
            self.arm_state = -1
        
        self.arm_publisher.publish(self.arm_state)
        time.sleep(self.time)

    def abre_garra(self):
        print("abrindo garra...")

        self.garra_state = -1
        self.garra_publisher.publish(self.garra_state)
        time.sleep(self.time)


    def fecha_garra(self):
        print("fechado garra...")

        self.garra_state = 0
        self.garra_publisher.publish(self.garra_state)
        time.sleep(self.time)
