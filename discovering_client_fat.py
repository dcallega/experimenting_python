import time
import socket
import threading
import _thread
import pickle
import net_utils_p3 as net

MESSAGE = "Oh bella ciao"
UDP_PORT = 5005
BUFF_SIZE = 1024

class EchoClient(threading.Thread):
  def __init__(self, ip='localhost', port=10000, name=""):
    threading.Thread.__init__(self)
    # Create a TCP/IP socket
    self.ip = ip
    self.name=name
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.buff_size = 16
    # Connect the socket to the port where the server is listening
    server_address = (ip, port)
    print('CLIENT ---> connecting to {} port {}'.format(*server_address))
    self.sock.connect(server_address)

  def run(self):
    try:
      # Send data
      # message = b'This is the message.  It will be repeated.'
      for _ in range(10):
        print('CLIENT {} ---> sending msg to {} {}'.format(self.ip, *self.sock.getsockname()))
        # self.sock.sendall(message)
        net.send_fat_msg(self.sock, pickle.dumps("SUPER"*100), timestamp=100, timestamp2=102)

        time.sleep(2)
        # # Look for the response
        # amount_received = 0
        # amount_expected = len(message)

        # while amount_received < amount_expected:
        #   data, other = self.sock.recvfrom(self.buff_size)
        #   amount_received += len(data)
        #   print('CLIENT {} ---> received {!r} from {}'.format(self.ip, data, other))
        # time.sleep(0.45)

    finally:  
      print('Closing socket')
      self.sock.close()


if __name__ == "__main__":
  sock = socket.socket(socket.AF_INET, # Internet
                       socket.SOCK_DGRAM) # UDP
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  while True:
    try:
      print(sock.getsockname())
      sock.sendto(MESSAGE.encode("utf-8"), ("<broadcast>", UDP_PORT))
      sock.settimeout(5)
      data, addr = sock.recvfrom(BUFF_SIZE)
      print("client received - {}".format(pickle.loads(data)))
      c = EchoClient(**pickle.loads(data))
      c.start()
    except socket.timeout as e:
      print("Socket timed out")
