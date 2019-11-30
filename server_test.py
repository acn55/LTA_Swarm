import socket
from multiprocessing import Process,Pipe
import time


serverPort = 12002

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print("The server is ready to receive")

running = True
alt = 100
coord = (13,45)
orient = 0
wp = [0,0,1,0]

try:
    while running:
        connectionSocket, addr = serverSocket.accept()
        message = connectionSocket.recv(1024).decode()
        print("received message: "+message)
        if message == "alt":
            # Requesting altitude
            return_msg = str(alt)
            alt += 1
        elif message == "coord":
            # Requesting x,y coordinates
            return_msg = str(coord)
            coord = (coord[0] + 1, coord[1])
        elif message == "orient":
            return_msg = str(orient)
            orient = (orient + 10) % 360
        elif message == "quit":
            return_msg = "quitting"
            running = False
        elif message == "forward":
            pass
        elif message == "backward":
            pass
        elif message == "right":
            pass
        elif message == "left":
            pass
        elif message == "up":
            pass
        elif message == "down":
            pass
        elif message.split(' ')[0] == "wp":
            wp[:] = [int(i) for i in message.split(' ')[1].split(',')]
        else:
            print("Not recognized")
            return_msg = "Not recognized"
        connectionSocket.send(return_msg.encode())
        connectionSocket.close()
    print ("running = {}".format(running))
    serverSocket.close()
except:
    serverSocket.close()
    raise
