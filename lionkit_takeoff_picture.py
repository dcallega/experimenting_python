'''
Created on Dec 13, 2017

@author: davide
'''
import threading
import time
import datetime
from compass import compass
import cv2
from pymavlink import mavutil
from config import *
from collections import deque
import uav_rccontrol
import thread
from config import *

NUMBER_OF_PICTURES = 3
try:
    connection_string = CONNECT_TO_VEHICLE
    drone = uav_rccontrol(connection_string)
    drone.set_mode('ALT_HOLD')
    drone.set_takeoff(1)
    capture = cv2.VideoCapture(0)
    for _ in range(NUMBER_OF_PICTURES):
        ret, img = capture.read()
        cv2.imwrite("./img/IMG" + str(int(time.time())) + ".jpg", img)
    time.sleep(2)
    drone.set_land()
except Exception as e:
    print e
finally:
    drone.stop()