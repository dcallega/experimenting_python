from pymavlink import mavutil # Needed for command message definitions
import time
import math
import sys
import numpy
import threading
import datetime as dt
import time
import uav_mavlink
from datetime import datetime
        
class  uav_rccontrol():

    def __init__(self, connection_string, uav, baud_rate=57600):
        
        ##################################################
        # Variables
        ##################################################
        self.up = up = 0
        self.takeoff = takeoff = 0
        self.samp_rate = samp_rate = 32000
        self.right = right = 0
        self.left = left = 0
        self.land = land = 0
        self.disarm = disarm = 0
        self.forward = forward = 0
        self.down = down = 0
        self.back = back = 0
        self.speed = speed = 200 #changed by sabur
        self.overridevalue0 = 1500
        self.overridevalue1 = 1500
        self.overridevalue2 = 1500
        self.data=[0]*8
        self.data[0]=self.overridevalue0
        self.data[1]=self.overridevalue1
        self.data[2]=self.overridevalue2
        self.mode = 'STABILIZE'
        self.duration = 1
        self.arm = 0
        self.connection_string= connection_string
        #self.connection_string='/dev/ttyUSB0'
        self.uav = uav#uav_mavlink.uav_mavlink(connection_string, baud_rate)
        #self.uav = uav_mavlink.uav_mavlink(connection_string, baud_rate)
        #Create 1 sec thread send
        self.running=True
        self.thread = threading.Thread(target=self.send_heartbeat)
        self.thread.daemon = True
        self.flying=0
        self.seq_no = 0
        self.thread.start()

    def get_up(self):
        return self.up

    def set_up(self, up):
      self.up = up
      if self.up==1:
        self.data[2]=self.overridevalue2+self.speed
        print('set_up: data', self.data)
        self.rc_override(self.data)
      if self.up==0:    
        self.data[2]=self.overridevalue2
        print('set_up: data', self.data)
        self.rc_override(self.data)
        
    def get_takeoff(self):
        return self.takeoff
    
    def rc_override(self,data):
        meta = 'rc_override'
        print('rc_overrride')
        print('rc_override: meta -',meta,' data -',data)
        self.seq_no+=1
        #msg += '%' + str(self.seq_no) + '%' + str(datetime.now())
        msg = '@' + meta + '%' + str(data) + '@' + str(self.seq_no) + '#' + str(datetime.now()) + '@'
        self.uav.command_handler(meta, data)
        #time.sleep(0.1)
        
    def set_takeoff(self, takeoff):
      print takeoff
      
      if(takeoff==1):
       meta = 'takeoff'
       if (self.mode == 'STABILIZE'):
           self.data[7]=0
       elif (self.mode == 'ALT_HOLD'):
           self.data[7]=1
       elif (self.mode == 'LOITER'):
           self.data[7]=2
       print('send_takeoff')
       print('set_takeoff: meta -',meta,' data -',self.data)
       self.seq_no += 1
       #msg += '%' + str(self.seq_no) + '%' + str(datetime.now())
       msg = '@' + meta + '%' + str(self.data) + '@' + str(self.seq_no) + '#' + str(datetime.now()) + '@'
       print ('Hey')
       print (self.uav)
       self.uav.command_handler(meta, self.data)
       print ('Hi')
       self.flying=1
            
    def get_samp_rate(self):
      return self.samp_rate

    def set_samp_rate(self, samp_rate):
      self.samp_rate = samp_rate

    def get_right(self):
      return self.right
        
    def set_right(self, right):
      self.right = right
      if self.right==1: #move
        self.data[0]=self.overridevalue0+self.speed
        print('set_right: data', self.data)
        self.rc_override(self.data)  
      if self.right==0:  #stop
        self.data[0]=self.overridevalue0
        print('set_right: data', self.data)
        self.rc_override(self.data)
       
    def get_left(self):
      return self.left

    def set_left(self, left):
      self.left = left
      if self.left==1: #move
        self.data[0]=self.overridevalue0-self.speed
        print('set_left: data', self.data)
        self.rc_override(self.data)
      if self.left==0:  #stop
        self.data[0]=self.overridevalue0
        print('set_left: data', self.data)
        self.rc_override(self.data)
               

    def get_land(self):
      return self.land
    
    def get_disarm(self):
      return self.disarm

    def set_land(self, land):
        self.land = land
        if  self.land==1:
          meta = 'land'
          print('send_land\n')
          #print('set_land: meta -',meta,' data -',self.data)
          self.seq_no += 1
          #msg += '%' + str(self.seq_no) + '%' + str(datetime.now())
          msg = '@' + meta + '%' + str(self.data) + '@' + str(self.seq_no) + '#' + str(datetime.now()) + '@'
          self.uav.command_handler(meta, self.data)
          self.flying=0
          self.land=0
          #time.sleep(0.1)


    def set_disarm(self, disarm):
        self.disarm = disarm
        if self.disarm==1:
          meta = 'disarm'
          print('send_disarm')
          #print('set_disarm: meta -',meta,' data -',self.data)
          self.seq_no += 1
          #msg += '%' + str(self.seq_no) + '%' + str(datetime.now()
          msg = '@' + meta + '%' + str(self.data) + '@' + str(self.seq_no) + '#' + str(datetime.now()) + '@'
          self.uav.command_handler(meta, self.data)
          self.disarm = 0
        
    def get_forward(self):
        return self.forward
               

    def set_forward(self, forward):
        self.forward = forward
        if self.forward==1: #move
           self.data[1]=self.overridevalue1-self.speed
           print('set_forward: data', self.data)
           self.rc_override(self.data)
        if self.forward==0:  #stop
           self.data[1]=self.overridevalue1
           print('set_forward: data', self.data)
           self.rc_override(self.data)
        
        
    def get_down(self):
        return self.down

    def set_down(self, down):
        self.down = down
        if self.down==1: #move
           self.data[2]=self.overridevalue2-self.speed
           print('set_down: data', self.data)
           self.rc_override(self.data)
        if self.down==0:  #stop
           self.data[2]=self.overridevalue2
           print('set_down: data', self.data)
           self.rc_override(self.data)
        
        
    def get_back(self):
        return self.back

    def set_back(self, back):
        self.back = back
        if self.back==1: #move
           self.data[1]=self.overridevalue1+self.speed
           print('set_back: data', self.data)
           self.rc_override(self.data)
        if self.back==0:  #stop
           self.data[1]=self.overridevalue1
           print('set_back: data', self.data)
           self.rc_override(self.data)
       
    def get_movement(self):
        return

    def set_movement(self, lr, fb, ud, duration, speed):
        if lr==1:
            self.data[0]=self.overridevalue0+self.speed
        elif lr==-1:
            self.data[0]=self.overridevalue0-self.speed
        else:
            self.data[0]=self.overridevalue0

        if fb==1:
            self.data[1]=self.overridevalue1+self.speed
        elif fb==-1:
            self.data[1]=self.overridevalue1-self.speed
        else:
            self.data[1]=self.overridevalue1

        if ud==1:
            self.data[2]=self.overridevalue2+self.speed
        elif ud==-1:
            self.data[2]=self.overridevalue2-self.speed
        else:
            self.data[2]=self.overridevalue2
        self.rc_override(self.data)
        time.sleep(duration);
        self.data[0]=self.overridevalue0 
        self.data[1]=self.overridevalue1 
        self.data[2]=self.overridevalue2 
        self.rc_override(self.data)

        
    def set_speed(self, speed):
        self.speed = speed
   
    def set_overridevalue0(self, value):
        self.overridevalue0 = value
    
    def set_overridevalue1(self, value):
        self.overridevalue1 = value
    
    def set_overridevalue2(self, value):
        self.overridevalue2 = value
    
    def get_speed(self):
        return self.speed
   
    def get_overridevalue0(self):
        return self.overridevalue0
    
    def get_overridevalue1(self):
        return self.overridevalue1
    
    def get_overridevalue2(self):
        return self.overridevalue2

    def get_mode(self):
        return self.mode

    def set_mode(self, mode):
        self.mode = mode

    def send_heartbeat(self):
        while(self.running):
          if self.flying==1:
            meta = 'heartbeat'
            print('send_heartbeat')
            #print('send_heartbeat: meta -',meta,' data -',self.data)
            self.seq_no += 1
            #msg += '%' + str(self.seq_no) + '%' + str(datetime.now())
            msg = '@' + meta + '%' + str(self.data) + '@' + str(self.seq_no) + '#' + str(datetime.now()) + '@'
            self.uav.command_handler(meta, self.data)
          time.sleep(1.0)
     
    def stop(self):
        thread.close()
        self.uav.stop()  

def main():
    print('Hey')


if __name__ == '__main__':
    main()
