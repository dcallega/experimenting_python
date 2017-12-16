'''
Created on Dec 14, 2017

@author: davide
'''
import time
import threading

ext_condition = threading.Condition()

class ext_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print "Initialized"
    def run(self):
        print "Start sleep"
        ext_condition.acquire()
        ext_condition.wait(5)
        print "Exit sleep"
    def other_func(self):
        print "This is another func"

if __name__ == '__main__':
    t1 = ext_thread()
    t1.start()
    time.sleep(0.1)
    t1.other_func()
    