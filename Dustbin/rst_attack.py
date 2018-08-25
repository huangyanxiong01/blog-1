import socket


HOST = '114.55.102.246'                 # Symbolic name meaning all available interfaces
PORT = 6666           # Arbitrary non-privileged port

# Symbolic name meaning all available interfaces
# HOST = '101.37.187.164'
# Arbitrary non-privileged port
# PORT = 443           

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.connect((HOST, PORT))

# l_onoff = 1                                                                                                                                                           
# l_linger = 0                                                                                                                                                          
# s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,                                                                                                                     
#              struct.pack('ii', l_onoff, l_linger))
# # send data here
# s.sendall('RST_PACKAGE')

while 1:
    try:
        l_onoff = 1                                                                                                                                                           
        l_linger = 0                                                                                                                                                          
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,                                                                                                                     
                     struct.pack('ii', l_onoff, l_linger))
        # send data here
        s.sendall('RST_PACKAGE')
    except Exception:
        pass

s.close()
