import threading
import _thread
import time
import socket
import pickle
from argparse import Namespace
import net_utils_p3 as net


UDP_DISCOVERY_PORT = 5005


class DiscoverableAnyInterfaceMultiClientsServer(threading.Thread):
  def __init__(self, conns, name="DiscoverableAnyInterfaceMultiClientsServer"):
    threading.Thread.__init__(self)
    self.discoverable_socket = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    self.discoverable_socket.bind(('', UDP_DISCOVERY_PORT))
    self.next_port = 11113
    self.my_tcp_ip = "127.0.0.1"
    self.conns = conns
    self.name = name

  def run(self):
    while True:
      print([(e, self.conns[e]) for e in self.conns])
      data, client_addr = self.discoverable_socket.recvfrom(1024) # buffer size is 1024 bytes
      if len(data) > 1 and (not(client_addr in self.conns) or self.conns[client_addr] == False):
        self.conns[client_addr] = True
        print("received message: {}".format(data.decode("utf-8")))
        self.discoverable_socket.sendto(pickle.dumps({"name":self.name, "ip": self.my_tcp_ip, "port": self.next_port}), client_addr)
        print("Address sent to {}:{}".format(*client_addr))
        e = EchoServerAny(ip=self.my_tcp_ip, port=self.next_port, conns=self.conns, client_addr=client_addr)
        self.next_port += 1
        e.start()
      else:
        time.sleep(0.1)
      data = ''

class EchoServerAny(threading.Thread):
  def __init__(self, ip='', port=10000, conns=None, client_addr=None):
    threading.Thread.__init__(self)
    # Create a TCP/IP socket
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.conns = conns
    self.client_addr = client_addr
    # Bind the socket to the address given on the command line
    server_address = (ip, port)
    self.sock.bind(server_address)
    print('starting up on {} port {}'.format(*self.sock.getsockname()))
    self.sock.listen(1)

  def run(self):
    rem = b""
    while True:
      print('waiting for a connection')
      self.connection, self.client_address = self.sock.accept()
      try:
        print('client connected:', self.client_address)
        while True:
          # data = self.connection.recv(16)
          # print('received {!r} from {}'.format(data, self.connection.getpeername()))
          # if data:
          #   self.connection.sendall(data)
          # else:
          #   break
          t1, t2, data, rem = net.receive_fat_msg(self.connection, rem)
          print(t1, t2)
          print(data)
      finally:
        self.conns[self.client_addr] = False
        print("Closing connection with {}".format(self.connection.getpeername()))
        self.connection.close()

if __name__=="__main__":
  
  d = DiscoverableAnyInterfaceMultiClientsServer(conns={})
  d.start()

