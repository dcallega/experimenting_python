'''
Created on Dec 3, 2017

@author: davide
'''
CONNECT_TO_VEHICLE = '/dev/ttyUSB0'
IMAGE_SIZE = (480,640)
X_CUTOFF = 0.02
Y_CUTOFF = 0.02
AREA_CUTOFF = 0.02
TARGET_AREA = 10000
DURATION = 1
#Set up velocity vector to map to each direction.
# vx > 0 => fly North
# vx < 0 => fly South
NORTH = 2
DURATION_N = DURATION
SOUTH = -2
DURATION_S = DURATION

# Note for vy:
# vy > 0 => fly East
# vy < 0 => fly West
EAST = 2
DURATION_E = DURATION
WEST = -2
DURATION_W = DURATION

# Note for vz: 
# vz < 0 => ascend
# vz > 0 => descend
UP = -0.5
DURATION_U = DURATION
DOWN = 0.5
DURATION_D = DURATION
    
TCP_IP_DRONE = '127.0.0.1'
TCP_IP_EDGE = '127.0.0.1'
TCP_PORT = 5007
BUFFER_SIZE = 256
DELIMITER = "DaViDe"

