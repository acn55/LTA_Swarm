import socket
from multiprocessing import Process,Pipe
import time


serverPort = 12002

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print("The server is ready to receive")

alt = 100

try:
    while True:
        connectionSocket, addr = serverSocket.accept()
        message = connectionSocket.recv(1024).decode()
        print("received message: "+message)
        if message == "alt":
            return_msg = str(alt)
            alt += 1
        else:
            return_msg = "Not alt"
        connectionSocket.send(return_msg.encode())
        connectionSocket.close()
    serverSocket.close()
except:
    serverSocket.close()
