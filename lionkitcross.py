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


time_started = time.time()
TIMEOUT = 10

try:
    connection_string = CONNECT_TO_VEHICLE
    drone = uav_rccontrol(connection_string)
    
    drone.set_mode('ALT_HOLD')
    drone.set_takeoff(1)
    time.sleep(2)
    
    drone.set_left(1)
    time.sleep(DURATION)
    drone.set_left(0)
    
    drone.set_up(1)
    time.sleep(DURATION)
    drone.set_up(0)
    
    drone.set_down(1)
    time.sleep(DURATION)
    drone.set_down(0)
    
    
    drone.set_land()
except Exception as e:
    print e
finally:
    drone.stop()