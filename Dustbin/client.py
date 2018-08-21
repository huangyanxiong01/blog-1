import socket
import time
import random


HOST = '10.211.55.25'    # The remote host
PORT = 6666              # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while 1:
    s.sendall(str(random.randint(1, 9999999999)))
    # data = s.recv(1024)
    # print 'Received', repr(data)
    time.sleep(0.5)
    # s.connect((HOST, PORT))

# s.sendall('Hello, world')
# data = s.recv(1024)
# print 'Received', repr(data)
# time.sleep(0.5)

s.close()


