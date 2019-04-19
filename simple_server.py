#!/usr/bin/env python

import socket
import argparse
import pickle

parser = argparse.ArgumentParser()
parser.add_argument("ip")
parser.add_argument("port")
args = parser.parse_args()

TCP_IP = args.ip
TCP_PORT = int(args.port)
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print('Connection address:', addr)
while True:
  print("waiting to receive")  
  data = conn.recv(BUFFER_SIZE)
  if not data: 
    continue
    time.sleep(0.1)
  print("received data:", pickle.loads(data))
  conn.send(pickle.dumps(pickle.loads(data)))
conn.close()