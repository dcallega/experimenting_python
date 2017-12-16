from __future__ import print_function
import numpy
import threading
import datetime as dt
import time
from pymavlink import mavutil
from builtins import object
import socket
import sys


class uav_mavlink():
    
    def __init__(self, connection_string,baud_rate=57600):
        self.connection_string=connection_string
        self.baud_rate=baud_rate
        self.mavlink_connection = mavutil.mavlink_connection(connection_string,baud=baud_rate)
        print (self.mavlink_connection)
       
        self.running=True
        self.takeoff=0
        self.data=data=[0]*8
        self.last_heartbeat_time=dt.datetime.now()

        ##print self.mavlink_connection
        self.thread = threading.Thread(target=self.check_for_message)
        self.thread.daemon = True
        self.thread.start()

        #Thread for heartbear
        self.thread3=threading.Thread(target=self.send_heartbeat)
        self.thread3.daemon = True
        self.thread3.start()
        print ('Hello')
 
    def command_handler(self, meta, data):
        print ('receive message')
        #print ('meta',meta)
        #print ('data',data)
        if meta == 'takeoff':
            print ('call takeoff')
            self.arm_and_takeoff(data)
        elif meta == 'rc_override':
            print ('rc_override')
            self.set_channel_overrides(data)
            self.data=data
        elif meta == 'land':
            print('land')
            self.set_land()
        elif meta == 'disarm':
            print('disarm')
            self.disarm() 
        elif meta == 'heartbeat':
            print('heartbeat')
            self.receive_hearbeat()

    def set_land(self):
        self.takeoff=0
        self.mavlink_connection.set_mode('LAND')
 
    def set_channel_overrides(self,data):
         #using set_overrides prevenet the controler of solo from taking command of a out of control UAS
         self.mavlink_connection.mav.rc_channels_override_send(
			self.mavlink_connection.target_system, self.mavlink_connection.target_component, *data)
 
    def disarm(self):
        self.data[0]=0
        self.data[1]=0
        self.data[2]=0
        self.mavlink_connection.arducopter_disarm()
    
    def receive_hearbeat(self):
        #print('heartbeat received')
        self.last_heartbeat_time=dt.datetime.now()
        #print(self.last_heartbeat_time)

    def arm_and_takeoff(self,data):
        if (self.takeoff==1):
            print ('currently in takeoff mode, switch to land mode before attempting again')
            return
        self.last_heartbeat_time=dt.datetime.now()
        print ("hold")
 
        #data=[0]*8
        #should be 1500 for alt_hold
        self.data[0]=data[0]
        self.data[1]=data[1]
        self.data[2]=data[2]
        
        print('before overide')
        #self.set_channel_overrides(self.data)
        time.sleep(0.5)
        #Get the motors working after arming (stablilze requires an input)
        #print('set servos')
        #self.mavlink2.set_relay(1)
        #self.mavlink2.set_relay(2)
        #self.mavlink2.set_relay(3)
        #self.mavlink2.set_servo(1,self.data[0])
        #self.mavlink2.set_servo(2,self.data[1])
        #self.mavlink2.set_servo(3,self.data[2])
        #print(self.data)
        #print('after servo')
        if(data[7]==0):
          self.mavlink_connection.set_mode('STABILIZE')
        elif(data[7]==1):
          self.mavlink_connection.set_mode('ALT_HOLD')
        elif(data[7]==2):
          self.mavlink_connection.set_mode('GUIDED')
          #self.mavlink_connection.set_mode('LOITER')
        time.sleep(0.5)
        print('first set')
        
        if not self.mavlink_connection.motors_armed(): # Function to check if UAV is armed
          print('in_Armed')
          self.mavlink_connection.arducopter_arm() # Function to ARM the UAV
          time.sleep(0.3)
          print('Armed called')
          #Do not proceed until the UAV is armed
          #self.mavlink2.motors_armed_wait() # Function to wait till the UAV is armed
          print ('Armed wait')
          
          #give up throttle
          #self.data[2]=self.data[2]+150
          tempdata=[0]*8
          tempdata[0]=data[0]
          tempdata[1]=data[1]
          tempdata[2]=data[2]
          tempdata[2]=tempdata[2]+200
          print('before override set')
          #self.set_servo(tempdata)
          self.set_channel_overrides(tempdata)
          
          print('after override')
        #current_location=self.mavlink_connection.location(True)
        #print ('current location: ',current_location)
        self.takeoff=1
          
    def mavlink_handler(self,msg):
        meta = pmt.car(msg)
        data = pmt.to_python(pmt.cdr(msg))
        binarrymavlink=bytearray(data)
        mavmessage=self.mavlink_connection.mav.decode(binarrymavlink)
        #print(mavmessage)
        self.mavlink_connection.write(binarrymavlink)
       
    def send_heartbeat(self):
        message = self.mavlink_connection.wait_heartbeat()
        while(self.running):
          if (self.takeoff!=0):
            currentimem5=dt.datetime.now()-dt.timedelta(seconds=5)
            print('in send_heartbeat')
            #print(currentimem5)
            #print(self.last_heartbeat_time)
            if(currentimem5>self.last_heartbeat_time): #if we have missed all messages for more than 5 seconds
              print('lost link')
              self.set_land()
              
            if (self.takeoff!=0):
              self.mavlink_connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                                  0, 0, 0)
              self.set_channel_overrides(self.data)
          time.sleep(1.0)
   
    def stop(self):
        self.running=False
        self.mavlink_connection.close()
        self.thread.close()
        self.thread1.close()       
        self.thread3.close()

    def __del__(self):
        self.running=False
        self.mavlink_connection.close()
        self.thread.close()
        self.thread1.close()       
        self.thread3.close()
        
    def check_for_message(self):
        # check_for_message is a thread reading the mavlink connection for messages, the actual device for this block
        while(self.running):
           #print ("check_for_message in thread")
           self.message=self.mavlink_connection.recv_match(blocking=True,timeout=10)
           #print('message: ',self.message)
           if self.message!=None:
            if self.message.get_type() == 'BAD_DATA':
                self.message=None
           if(self.message!=None):
             #print ("message found serial")
             #print (self.message)
             buf=self.message.get_msgbuf()
             bufnp=numpy.frombuffer(buf,dtype=numpy.uint8)
             print (bufnp) 
             #self.message_port_pub(pmt.intern("MAVLink_OUT"),pmt.cons(pmt.PMT_NIL,pmt.to_pmt(bufnp)))
             self.message=None    



