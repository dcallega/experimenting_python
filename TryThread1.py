'''
Created on Dec 4, 2017

@author: davide
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
TIMEOUT = 120.0
t_pos = [0,0,0]
global keyboard_input
condition_cap_det = threading.Condition()
condition_det_mov = threading.Condition()


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
        time_started = time.time()
        while time.time()-time_started < TIMEOUT:
            condition_cap_det.acquire()
            if self.verbose:
                print 'Condition acquired'
            ret, image = self.capture.read()
            if ret:
                if(len(self.queue) > 4):
                    self.queue.pop()
                self.queue.appendleft(image)
            if self.verbose:
                print '%d appended to list by %s' % (1, self.name)
                print 'condition notified by %s' % self.name
            condition_cap_det.notify()
            if self.verbose:
                print 'condition released by %s' % self.name
            condition_cap_det.release()
            time.sleep(DURATION/3)
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
        time_started = time.time()
        while time.time()-time_started < TIMEOUT:
            condition_cap_det.acquire()
            if self.verbose:
                print 'condition acquired by %s' % self.name
            ret_img = True
            while True:
                if self.queue:
                    if self.verbose:
                        print(len(self.queue))
                    image = self.queue.pop()
                    condition_det_mov.acquire()
                    if ret_img:
                        t_pos[0], t_pos[1], t_pos[2], image = self.detector.direction2center(image, True)
                        cv2.imwrite("20171205.jpg", image)
                    else:
                        t_pos[0], t_pos[1], t_pos[2] = self.detector.direction2center(image)
                    condition_det_mov.notify()
                    if self.verbose:
                        print("Notified")
                    classified_image = image
                    if self.verbose:
                        print(dx,dy,area)
                    condition_det_mov.release()
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
            
class Movement (threading.Thread):
    def __init__(self, string_connection = None, verbose = VERBOSE):
        threading.Thread.__init__(self)
        self.name = "Movement"
        self.verbose = verbose
        self.is_running = False
        if(string_connection is not None):
            self.vehicle = connect(string_connection, wait_ready=True) 
        else:
            self.vehicle = None 
        
    
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
    
    def run(self):
        self.is_running = True
        if self.vehicle is not None:
            self.arm_and_takeoff(20)
            print("Taking off")
        time_started = time.time()
        while time.time()-time_started < TIMEOUT and self.is_running:
            x_action, y_action, z_action = 0,0,0
            condition_det_mov.acquire()
            condition_det_mov.wait()
            if self.verbose:
                print("Got notification")
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
                pass
            print(x_action, y_action, z_action, DURATION)
            condition_det_mov.release()
            self.send_ned_velocity(x_action,y_action,z_action,DURATION)
            self.send_ned_velocity(0,0,0,DURATION)
        self.is_running = False
        self.stop()
    
    def stop(self):
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
            self.stop()
        
    
class Keyboard (threading.Thread):
    def __init__(self, movement_thread = None):
        threading.Thread.__init__(self)
        self.is_running = False
        self.movement_thread = movement_thread
    def raw_input_with_timeout(self, prompt, timeout=30.0):
        print prompt,    
        timer = threading.Timer(timeout, thread.interrupt_main)
        astring = None
        try:
            timer.start()
            astring = raw_input(prompt)
        except KeyboardInterrupt:
            pass
        timer.cancel()
        return astring
    def run(self):
        self.is_running = True
        while t1.is_running:
            keyboard_input = self.raw_input_with_timeout("Type command below")
            print "You typed " + keyboard_input
            self.movement_thread.execute_keyboard(keyboard_input)
            keyboard_input = None
        self.is_running = False
        self.stop()
    def stop(self):
        self.is_running = False
        keyboard_input = None
    
try:
    integers = deque([])
    keyboard_input = None
#     connection_string = '127.0.0.1:14550'
    connection_string = None
    if not connection_string:
        import dronekit_sitl
        sitl = dronekit_sitl.start_default()
        connection_string = sitl.connection_string()
    t1 = Image_capture(integers)
    t2 = Face_detector(integers)
    t3 = Movement(string_connection = connection_string)
    t4 = Keyboard(movement_thread = t3)
    
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    print 'Threads started'
    while t1.is_running and t2.is_running and t3.is_running:
#         cv2.imshow('Frame', cv2.imread('20171205.jpg',0))
        pass
    print 'Exiting'
except Exception:
    print("Exception occurred")
finally:
    cv2.destroyAllWindows()
#     condition_det_mov.release()
#     condition_cap_det.release()
    t1.stop()
    t2.stop()
    t3.stop()
    t4.stop()
    print(t1.is_running, t2.is_running,t3.is_running,t4.is_running)
    t1.join()
    print("t1 joined")
    t2.join()
    print("t2 joined")
    t3.join()
    print("t3 joined")
    t4.join()
    print("t4 joined")
    print 'Exiting'
