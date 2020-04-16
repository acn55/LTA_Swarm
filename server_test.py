import socket
from multiprocessing import Process,Pipe
import time


serverPort = 12002

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind(('127.0.0.1',serverPort))
serverSocket.listen(1)
print("The server is ready to receive")

running = True
alt = 0
coord = (0,0)
orient = 0
wp = [0,0,1,0] # Current waypoint
op_mode = 0 # 0: full auto, 1: waypoint, 2: manual
ATs = [[1,2.3,0.5],[5,1.1,-0.2]]

try:
    while running:
        connectionSocket, addr = serverSocket.accept()
        message = connectionSocket.recv(1024).decode()
        print("received message: "+message)
        if message == "alt":
            # Requesting altitude
            return_msg = str(alt)
        elif message == "coord":
            # Requesting x,y coordinates
            return_msg = str(coord)
        elif message == "orient":
            return_msg = str(orient)
        elif message == "quit":
            # Close server (debugging)
            return_msg = "quitting"
            running = False
        elif message == "forward":
            # Manual command move forward
            pass
        elif message == "backward":
            # Manual command move backward
            pass
        elif message == "right":
            # Manual command pivot right
            pass
        elif message == "left":
            # Manual command pivot left
            pass
        elif message == "up":
            # Manual command increase altitude
            pass
        elif message == "down":
            # Manual command decrease altitude
            pass
        elif message == "stop":
            # Manual command stop motors
            pass
        elif message == "curr wp":
            # Requesting current waypoint
            return_msg = str(wp[0]) + "," + str(wp[1]) + "," + str(wp[2]) + "," + str(wp[3])
        elif message.split(' ')[0] == "mode":
            op_mode = int(message.split(' ')[1])
            print("new op mode: " + str(op_mode))
        elif message.split(' ')[0] == "wp":
            # Waypoint command set new waypoint
            wp[:] = [int(i) for i in message.split(' ')[1].split(',')]
        elif message == "ats":
            # Requesting AprilTag data
            numATs = len(ATs)
            return_msg = str(numATs)
            for a in ATs:
                for i in a:
                    return_msg += "," + str(i)
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
