import socket
from multiprocessing import Process,Pipe
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(17,GPIO.OUT) #left
GPIO.setup(18,GPIO.OUT) #right
GPIO.setup(22,GPIO.OUT) #top
GPIO.setup(23,GPIO.OUT) #bot
GPIO.setup(27,GPIO.OUT) #LED

#set pwm value
freq1 = freq2 = freq3 = freq4 = 100
dc1 = dc2 = dc3 =dc4 = 0
p=GPIO.PWM(17,freq1)
pwm=GPIO.PWM(18,freq2)
pto=GPIO.PWM(22,freq3)
pbo=GPIO.PWM(23,freq4)
p.start(dc1)
pwm.start(dc2)
pto.start(dc3)
pbo.start(dc4)
fled = 1
pled=GPIO.PWM(27,fled)
dcled=50
pled.start(dcled)

serverPort = 12002
serverIP = '10.148.2.203'

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind((serverIP,serverPort))
serverSocket.listen(1)
print("The server is ready to receive")
#set the initial logic output
def right():
	dc1=0
	p.ChangeDutyCycle(dc1)
	pwm.ChangeDutyCycle(dc2)
def left():
	dc2=0
	p.ChangeDutyCycle(dc1)
	pwm.ChangeDutyCycle(dc2)
def top():
	dc4=0
	pto.ChangeDutyCycle(dc3)
	pbo.ChangeDutyCycle(dc4)
def bot():
	dc3=0
	pto.ChangeDutyCycle(dc3)
	pbo.ChangeDutyCycle(dc4)
def forward():
	p.ChangeDutyCycle(dc1)
	pwm.ChangeDutyCycle(dc2)
	
buff1 = buff2 = buff3 = buff4 = buff5 = buff6 = buff7 = 0
keep_going = False
keep = False
keep_up = False
keep_down = False
keep_for = False
running = True
alt = 100
coord = (13,45)
orient = 0
wp = [0,0,1,0] # Current waypoint
op_mode = 0 # 0: full auto, 1: waypoint, 2: manual

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
            # Close server (debugging)
            return_msg = "quitting"
            p.stop()
            pwm.stop()
            pto.stop()
            pbo.stop()
            GPIO.cleanup()
            running = False
        elif message == "forward":
            # Manual command move forward
            keep_for = True
            pass
        elif message == "backward":
            # Manual command move backward
            pass
        elif message == "right":
            # Manual command pivot right
            keep = True
            pass
        elif message == "left":
            # Manual command pivot left
            dc1=90
            left()
            #keep_going = True
            pass
        elif message == "up":
            # Manual command increase altitude
            keep_up = True
            pass
        elif message == "down":
            # Manual command decrease altitude
            keep_down = True
            pass
        elif message == "stop":
            # Manual command stop motors
            dc1 = 0 
            dc2 = 0
            buff1 = buff2 = buff3 = buff4 = 0
            right()
            left()
            forward()
            dc3 = dc4 = 0
            buff5 = buff6 = buff7 = 0
            top()
            bot()
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
        else:
            print("Not recognized")
            return_msg = "Not recognized"
        while keep_going: #left
			if buff1 == 0:
				dc1 = 90
				buff3 = 1
			print 'left'
			left()
			buff1 = 1
			buff4 = 0
			buff2 = 0
			keep_going =False
        while keep: #right
            if buff2 == 0:
                dc2 = 90
                buff3 = 1
            print 'right'
            right()
            buff1 = buff4 = 0
            buff2 =1
            keep = False
        while keep_for: #forward
            if buff4 == 0:
                dc2 = dc1 = 90
                buff3 = 1
            print 'forward'
            forward()
            buff1 = buff2 = 0
            buff4 =1
            keep_for = False
        while keep_up: #up
            if buff5 == 0:
                dc3 = 90
                buff7 = 1
            print 'up'
            top()
            buff6 = 0
            buff5 =1
            keep_up = False
        while keep_down: #down
            if buff6 == 0:
                dc4 = 90
                buff7 = 1
            print 'down'
            bot()
            buff6 = 1
            buff5 =0
            keep_down = False

		
        connectionSocket.send(return_msg.encode())
        connectionSocket.close()
    print ("running = {}".format(running))
    serverSocket.close()
except:
    serverSocket.close()
    raise
