import time
import socket
import threading
import _thread

MESSAGE = "Oh bella ciao"
UDP_PORT = 5005

class EchoClient(threading.Thread):
  def __init__(self, ip='localhost', port=10000):
    threading.Thread.__init__(self)
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
      for _ in range(10):
        print('CLIENT {} ---> sending {!r} to {} {}'.format(self.ip, message, *self.sock.getsockname()))
        self.sock.sendall(message)

        # Look for the response
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
          data, other = self.sock.recvfrom(self.buff_size)
          amount_received += len(data)
          print('CLIENT {} ---> received {!r} from {}'.format(self.ip, data, other))
        time.sleep(0.45)

    finally:  
      print('Closing socket')
      self.sock.close()


if __name__ == "__main__":
  sock = socket.socket(socket.AF_INET, # Internet
                       socket.SOCK_DGRAM) # UDP
  while True:
    try:
      sock.sendto(MESSAGE.encode("utf-8"), ("", UDP_PORT))
      sock.settimeout(5)
      data, addr = sock.recvfrom(1024)
      print("client received - {}".format(data.decode("utf-8")))
      c = EchoClient(ip=data.decode("utf-8").split(":")[0], port=int(data.decode("utf-8").split(":")[1]))
      c.start()
    except socket.timeout as e:
      print("Socket timed out")


  # sock_tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # sock_tcp_client.connect((data.decode("utf-8").split(":")[0], int(data.decode("utf-8").split(":")[1])))
  # print("client_connectet to :", addr)
  # sock_tcp_client.sendall(b"bubi")
  # sock_tcp_client.close()
  # time.sleep(2)
