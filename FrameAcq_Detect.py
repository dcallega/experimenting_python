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

class myThread (threading.Thread):
    def __init__(self, name, counter, lock = None, function):
        threading.Thread.__init__(self)
        self.threadID = counter
        self.name = name
        self.counter = counter
        if lock is None:
            lock = threading.Lock()
        self.lock = lock
        time.sleep(3)
    def run(self):
        print "Starting " + self.name
        # Acquire lock to synchronize thread
        self.lock.acquire()
        try:
            print_date(self.name, self.counter)
            time.sleep(2)
            # Release lock for the next thread
        finally:
            self.lock.release()
        print "Exiting " + self.name
        


def print_date(threadName, counter):
    datefields = []
    today = datetime.date.today()
    datefields.append(today)
    print "%s[%d]: %s" % ( threadName, counter, datefields[0] )

times = []
lock_ = threading.Lock()
# Create new threads
times.append(time.time())
thread1 = myThread("Thread", 1)
times.append(time.time())
thread2 = myThread("Thread", 2)

print("Before launching threads")


# Start new Threads
times.append(time.time())
thread1.start()
times.append(time.time())
thread2.start()
times.append(time.time())

thread1.join()
times.append(time.time())
thread2.join()
times.append(time.time())
pred = times[0]
for e in times:
    print(e - pred)
    pred = e
print "Exiting the Program!!!"