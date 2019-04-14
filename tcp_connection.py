import socket
import sys
from threading import Thread
import time
import _thread

class EchoServer(Thread):
  def __init__(self, ip='localhost', port=10000):
    Thread.__init__(self)
    # Create a TCP/IP socket
    self.buff_size = 16
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (ip, port)
    print('SERVER ---> starting up on {} port {}'.format(*server_address))
    self.sock.bind(server_address)

    # Listen for incoming connections
    self.sock.listen(1)

  def run(self):
    while True:
      # Wait for a connection
      print('SERVER ---> waiting for a connection')
      self.connection, self.client_address = self.sock.accept()
      try:
        print('SERVER ---> connection from', self.client_address)
        # Receive the data in small chunks and retransmit it
        while True:
          data = self.connection.recv(self.buff_size)
          print('SERVER ---> received {!r}'.format(data))
          if data:
            print('SERVER ---> sending data back to the client')
            self.connection.sendall(data)
          else:
            print('SERVER ---> no data from', self.client_address)
            break
      finally:
          # Clean up the connection
          self.connection.close()

class EchoClient(Thread):
  def __init__(self, ip='localhost', port=10000):
    Thread.__init__(self)
    # Create a TCP/IP socket
    self.ip = ip
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.buff_size = 16
    # Connect the socket to the port where the server is listening
    server_address = (ip, port)
    print('CLIENT ---> connecting to {} port {}'.format(*server_address))
    self.sock.connect(server_address)

  def run(self):
    try:
      # Send data
      message = b'This is the message.  It will be repeated.'
      print('CLIENT {} ---> sending {!r} to {} {}'.format(self.ip, message, *self.sock.getsockname()))
      for _ in range(1):
        self.sock.sendall(message)

        # Look for the response
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
          data, other = self.sock.recvfrom(self.buff_size)
          amount_received += len(data)
          print('CLIENT {} ---> received {!r} from {}'.format(self.ip, data, other))
        time.sleep(1)

    finally:  
      print('closing socket')
      self.sock.close()

class EchoServerAny(Thread):
  def __init__(self, ip='', port=10000):
    Thread.__init__(self)
    # Create a TCP/IP socket
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the address given on the command line
    server_address = (ip, port)
    self.sock.bind(server_address)
    print('starting up on {} port {}'.format(*self.sock.getsockname()))
    self.sock.listen(1)

  def run(self):
    while True:
      print('waiting for a connection')
      self.connection, self.client_address = self.sock.accept()
      try:
        print('client connected:', self.client_address)
        while True:
          data, other = self.connection.recvfrom(16)
          print('received {!r} from {}'.format(data, other))
          if data:
            self.connection.sendall(data)
          else:
            break
      finally:
        self.connection.close()


class EchoServerAnyMultipleConnections(Thread):
  def __init__(self, ip='', port=10000):
    Thread.__init__(self)
    # Create a TCP/IP socket
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the address given on the command line
    server_address = (ip, port)
    self.sock.bind(server_address)
    print('SERVER --> starting up on {} port {}'.format(*self.sock.getsockname()))
    self.sock.listen(1)

  def run(self):
    while True:
      print('SERVER --> waiting for a connection')
      connection, client_address = self.sock.accept()
      _thread.start_new_thread(self.on_new_connection, (connection, client_address))
      
  def on_new_connection(self,client_sock,addr):
    try:
      print('SERVER --> client connected:', addr)
      while True:
        data = client_sock.recv(16)
        print('SERVER --> received {!r} from {}'.format(data, client_sock.getpeername()))
        if data:
          print('SERVER --> Send {!r} to {}'.format(data, client_sock.getpeername()))
          client_sock.sendall(data)
        else:
          break
    finally:
      client_sock.close()


if __name__ == "__main__":
  # s = EchoServerAnyMultipleConnections()
  # c = EchoClient(ip='127.0.0.1')
  # s.start()
  # c.start()
  c2 = EchoClient(ip = "128.195.55.200")
  c2.start()
  while True:
    time.sleep(0.5)

