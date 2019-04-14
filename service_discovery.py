import time
import socket
import _thread


my_ip = "127.0.0.1"
next_usable_port = 11111

def serve(sock):
  global next_usable_port
  while True:
    data, client_addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: {}".format(data.decode("utf-8")))
    sock.sendto(("{}:{}".format(my_ip, next_usable_port)).encode("utf-8"), client_addr)
    sock_tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("here", my_ip, next_usable_port)
    my_addr = (my_ip, next_usable_port)
    sock_tcp_server.bind(my_addr)
    next_usable_port += 1
    _thread.start_new_thread(handle_tcp, (client_addr, sock_tcp_server))
  
def handle_tcp(client_addr, my_sock):
  my_sock.listen(1)
  client_conn, client_address = my_sock.accept()
  try:
    print('SERVER --> client connected:', addr)
    while True:
      data = client_conn.recv(16)
      print('SERVER --> received {!r} from {}'.format(data, client_conn.getpeername()))
      if data:
        print('SERVER --> Send {!r} to {}'.format(data, client_conn.getpeername()))
        client_conn.sendall(data)
      else:
        break
  finally:
    client_conn.close()


UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"Hello, World!"

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("message: {}".format(MESSAGE))

sock_server = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock_server.bind(('', UDP_PORT))
_thread.start_new_thread(serve, (sock_server, ))

for i in range(5):
  sock = socket.socket(socket.AF_INET, # Internet
                       socket.SOCK_DGRAM) # UDP
  sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
  sock.settimeout(5)
  data, addr = sock.recvfrom(1024)
  print("client received - {}".format(data.decode("utf-8")))
  sock_tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock_tcp_client.connect((data.decode("utf-8").split(":")[0], int(data.decode("utf-8").split(":")[1])))
  print("client_connectet to :", addr)
  sock_tcp_client.sendall(b"bubi")
  sock_tcp_client.close()
  time.sleep(2)









