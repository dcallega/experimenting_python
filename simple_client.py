#!/usr/bin/env python

import socket
import argparse
import time
import _thread
import pickle



def echo_service(sock):
  while(True):
    print("in echo_service")
    sock.send(pickle.dumps(MESSAGE))
    print("Message sent, waiting to receive")
    data = sock.recv(BUFFER_SIZE)
    print("received data:", pickle.loads(data))
    time.sleep(1)
  sock.close()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip0")
  parser.add_argument("--port0")
  parser.add_argument("--ip1")
  parser.add_argument("--port1")
  args = parser.parse_args()

  TCP_IP = (args.ip0, args.ip1)
  TCP_PORT = (int(args.port0), int(args.port1))
  BUFFER_SIZE = 1024
  MESSAGE = "Hello, World!"
  s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s1.connect((TCP_IP[0], TCP_PORT[0]))
  s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s2.connect((TCP_IP[1], TCP_PORT[1]))
  _thread.start_new_thread(echo_service, (s1, ))
  _thread.start_new_thread(echo_service, (s2, ))
  while True:
    time.sleep(1)