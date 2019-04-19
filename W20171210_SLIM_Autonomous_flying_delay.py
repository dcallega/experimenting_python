'''
Created on Dec 4, 2017

@author: Davide Callegaro
'''
#Python multithreading example to print current date.
#1. Define a subclass using Thread class.
#2. Instantiate the subclass and trigger the thread. 

import threading
import time
import datetime
from compass import compass
import cv2
from dronekit import connect, VehicleMode
from pymavlink import mavutil
from config import *
from collections import deque
import thread

classified_image = None
VERBOSE = False
TIMEOUT = 60.0
t_pos = [0,0,0]
global keyboard_input
condition_cap_det = threading.Condition()
condition_det_mov = threading.Condition()
time_started = time.time()
global decision_queue
decision_queue = deque([])
global frame_time_gener
datafile = open("./logs/AUTO_dist_delay.csv", "w")

class Image_capture (threading.Thread):
    def __init__(self, queue, verbose = VERBOSE):
        threading.Thread.__init__(self)
        self.capture = cv2.VideoCapture(0)
        self.queue = queue
        self.name = "Capturer"
        self.verbose = verbose
        self.is_running = False
    def run(self):
        self.is_running = True
        while time.time()-time_started < TIMEOUT and self.is_running:
            #print(str(time.time()-time_started) + " < " + str(TIMEOUT))
            condition_cap_det.acquire()
            if self.verbose:
                print 'Condition acquired'
            ret, image = self.capture.read()
            if ret:
                if(len(self.queue) > 4):
                    self.queue.pop()
                self.queue.appendleft((image, time.time()))
            if self.verbose:
                print '%d appended to list by %s' % (1, self.name)
                print 'condition notified by %s' % self.name
            condition_cap_det.notify()
            if self.verbose:
                print 'condition released by %s' % self.name
            condition_cap_det.release()
        self.is_running = False
        self.stop()
    def stop(self):
        self.is_running = False
        print('Stop ' + self.name)
        self.capture.release()
        cv2.destroyAllWindows()
        
class Face_detector (threading.Thread):
    def __init__(self, queue, verbose = VERBOSE):
        threading.Thread.__init__(self)
        self.queue = queue
        self.detector = compass(do_show_image=False)
        self.name = "Detector"  
        self.verbose = verbose
        self.is_running = False
    def run(self):
        """
        Thread run method. Consumes integers from list
        """
        counter = 0
        self.is_running = True
        while time.time()-time_started < TIMEOUT and self.is_running:
            #print(str(time.time()-time_started) + " < " + str(TIMEOUT))
            condition_cap_det.acquire()
            if self.verbose:
                print 'condition acquired by %s' % self.name
            ret_img = True
            while True:
                if self.queue:
                    if self.verbose:
                        print(len(self.queue))
                    (image,generation_time) = self.queue.pop()
                    condition_det_mov.acquire()
                    if ret_img:
                        t_pos[0], t_pos[1], t_pos[2], image = self.detector.direction2center(image, True)
                        cv2.imwrite("20171205.jpg", image)
                    else:
                        t_pos[0], t_pos[1], t_pos[2] = self.detector.direction2center(image)
                    frame_time_gener = generation_time
                    condition_det_mov.notify()
                    if self.verbose:
                        print("Notified")
                    classified_image = image
                    if self.verbose:
                        print(t_pos[0], t_pos[1], t_pos[2])
                    global decision_queue
                    decision_queue.appendleft((t_pos[0], t_pos[1], t_pos[2], generation_time))
                    condition_det_mov.release()
#                     print("face detected")
#                     print decision_queue
                    if self.verbose:
                        print '%d popped from list by %s' % (1, self.name)
                    break
                if self.verbose:
                    print 'condition wait by %s' % self.name
                condition_cap_det.wait()
            if self.verbose:
                print 'condition released by %s' % self.name
            condition_cap_det.release()
        self.is_running = False
        self.stop()
    def stop(self):
        self.is_running = False
        print('Stop ' + self.name)

class Movement:
    def __init__(self, string_connection = None, verbose = VERBOSE):
        self.name = "Movement"
        self.verbose = verbose
#         self.vehicle.mode = VehicleMode("LOITER")
        if(string_connection is not None):
            self.vehicle = connect(string_connection, wait_ready=True) 
        else:
            self.vehicle = None
        self.last_action = (0,0,0, time.time())
    
    def arm_and_takeoff(self,aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """
    
        print("Basic pre-arm checks")
        # Don't let the user try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(DURATION)
    
            
        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
    
        while not self.vehicle.armed:      
            print(" Waiting for arming...")
            time.sleep(DURATION)
    
        print("Taking off!")
        self.vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude
    
        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            #print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)      
            if self.vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
                print("Reached target altitude")
                break
            time.sleep(DURATION)
    
    def send_ned_velocity(self,velocity_x, velocity_y, velocity_z, duration):
        """
        Move vehicle in direction based on specified velocity vectors and
        for the specified duration.
    
        This uses the SET_POSITION_TARGET_LOCAL_NED command with a type mask enabling only 
        velocity components 
        (http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/#set_position_target_local_ned).
        
        Note that from AC3.3 the message should be re-sent every second (after about 3 seconds
        with no message the velocity will drop back to zero). In AC3.2.1 and earlier the specified
        velocity persists until it is canceled. The code below should work on either version 
        (sending the message multiple times does not cause problems).
        
        See the above link for information on the type_mask (0=enable, 1=ignore). 
        At time of writing, acceleration and yaw bits are ignored.
        """
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
            0b0000111111000111, # type_mask (only speeds enabled)
            0, 0, 0, # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
            0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 
    
        # send command to vehicle on 10 Hz cycle
        tmp = int(duration*2)
        for _ in range(0,tmp):
            self.vehicle.send_mavlink(msg)
            time.sleep(.5)
    
    def move(self, dx, dy, dz, timestamp_frame):
        x_action, y_action, z_action = 0,0,0
        if self.verbose:
            print("Called for action", [str(e) for e in [dx, dy, dz, timestamp_frame]])
        if abs(t_pos[0]) > X_CUTOFF:       #does it make sense to move?
            if t_pos[0] > 0:              #target on my left?
                x_action = WEST
            else:
                x_action = EAST
        if abs(t_pos[1]) > Y_CUTOFF:
            if t_pos[1] > 0:              #target up?
                y_action = UP
            else:
                y_action = DOWN
        if abs((t_pos[2] - TARGET_AREA)/TARGET_AREA) > AREA_CUTOFF:
            if(t_pos[2] - TARGET_AREA) > 0:
                z_action = SOUTH
            else:
                z_action = NORTH
        print(x_action, y_action, z_action, DURATION)
        
        time_diff = time.time() - timestamp_frame
        print("Taking action after " + str(time_diff))
        datafile.write(','.join([str(e) for e in [dx,dy,dz,time_diff]]) + "\n")
        self.send_ned_velocity(x_action,y_action,z_action,DURATION)
        self.send_ned_velocity(0,0,0,DURATION)
    
    def close(self):
        self.is_running = False
        print('Stop ' + self.name)
        print("In STOP function: Landing")
        self.vehicle.mode = VehicleMode("LAND")
        self.vehicle.close()
          
    def execute_keyboard(self, command_received = None):
        if command_received == 'L':
            print("Typed landing")
            print("Start landing")
            self.vehicle.mode = VehicleMode("LAND")
            self.running = False
            self.stop()
        elif command_received == 'l':
            print('Left')
            self.send_ned_velocity(WEST,0,0,DURATION)
            self.send_ned_velocity(0,0,0,DURATION)
        elif command_received == 'r':
            print("Right")
            self.send_ned_velocity(EAST,0,0,DURATION)
            self.send_ned_velocity(0,0,0,DURATION)
        elif command_received == 'u':
            print("Up")
            self.send_ned_velocity(0,UP,0,DURATION)
            self.send_ned_velocity(0,0,0,DURATION)
        elif command_received == 'd':
            print("Down")
            self.send_ned_velocity(0,DOWN,0,DURATION)
            self.send_ned_velocity(0,0,0,DURATION)
        elif command_received == 'b':
            print("Backwards")
            self.send_ned_velocity(0,0,SOUTH,DURATION)
            self.send_ned_velocity(0,0,0,DURATION)
        elif command_received == 'f':
            print("Forward")
            self.send_ned_velocity(0,0,NORTH,DURATION)
            self.send_ned_velocity(0,0,0,DURATION)
        else:
            print("Typed ELSE")
            print("Start landing")
            self.vehicle.mode = VehicleMode("LAND")
            self.running = False
            self.close()
        
        
class DecisionManager(threading.Thread):
    def __init__(self, movement_thread):
        threading.Thread.__init__(self)
        self.last_decision_taken = (0,0,0,time.time())
        self.drone = movement_thread
        self.name = "Decision manager"
        self.is_running = False
        
    def start(self):
        self.run()
    def run(self):
        self.is_running = True
        print(self.name + " is running")
        while time.time()-time_started and self.is_running:
            condition_det_mov.acquire()
            if(len(decision_queue) > 0):
                global decision_queue
                print(decision_queue)
                a,b,c,d = decision_queue[-1]
                decision_queue = deque([])
                x,y,z,time_frame_aa = a,b,c,d
                drone.move(x,y,z,time_frame_aa)
                print(self.name + " executed action")
                condition_det_mov.release()
                continue
            condition_det_mov.wait()
            print(self.name + " is waiting")
        self.is_running = False
        
    def stop(self):
        self.is_running = False
                
        
class Keyboard (threading.Thread):
    def __init__(self, drone = None):
        threading.Thread.__init__(self)
        self.is_running = False
        self.drone = drone
    def run(self):
        self.is_running = True
        while time.time()-time_started < TIMEOUT and self.is_running:
            keyboard_input = raw_input("Type command below")
            print "You typed " + keyboard_input
            self.drone.execute_keyboard(keyboard_input)
            keyboard_input = None
        self.is_running = False
        self.stop()
    def stop(self):
        self.is_running = False
        keyboard_input = None

try:
    integers = deque([])
    decision_queue = deque([])
    keyboard_input = None
#     connection_string = '127.0.0.1:14550'
    connection_string = None
    if not connection_string:
        import dronekit_sitl
        sitl = dronekit_sitl.start_default()
        connection_string = sitl.connection_string()
    t1 = Image_capture(integers)
    t2 = Face_detector(integers, decision_queue)
    drone = Movement(connection_string)
    t3 = DecisionManager(drone)
    t4 = Keyboard(drone)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    drone.arm_and_takeoff(10)
    time_started = time.time()
    print 'Threads started'
    while t1.is_running and t2.is_running and t3.is_running and t4.is_running:
#         print(t1.is_running , t2.is_running , t4.is_running)
        time.sleep(1)
    print 'Exiting'
except Exception as e:
    print("Exception occurred")
    print e
finally:
    cv2.destroyAllWindows()
#     condition_det_mov.release()
#     condition_cap_det.release()
    t1.stop()
    t2.stop()
    t3.stop()
    t4.stop()
    print(t1.is_running, t2.is_running,t4.is_running)
    t1.join(TIMEOUT)
    print("t1 joined")
    t2.join(TIMEOUT)
    t3.join(TIMEOUT)
    drone.close()
    print("t2 joined")
    t4.join(TIMEOUT)
    datafile.close()
    print("t4 joined")
    print 'Exiting'
