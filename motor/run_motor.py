import time 
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(17,GPIO.OUT) #left
GPIO.setup(18,GPIO.OUT) #right
GPIO.setup(22,GPIO.OUT) #top



#set pwm value
freq1= 100
dc1=0
freq2= 100
dc2=0
freq3= 100
dc3=0
p=GPIO.PWM(17,freq1)
pwm=GPIO.PWM(18,freq2)
pto=GPIO.PWM(22,freq3)

p.start(dc1)
pwm.start(dc2)
pto.start(dc3)
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
	pto.ChangeDutyCycle(dc3)
def forward():
	p.ChangeDutyCycle(dc1)
	pwm.ChangeDutyCycle(dc2)
	
buff1 = 0
buff2 = 0
buff3 = 0
buff4 = 0
buff5 = 0
keep_going = False
keep = False
keep_up = False
keep_for = False
try:
	
	while True:
		print dc1,dc2, dc3
		command =raw_input("input:")
		if command == 'a': #turn left
			keep_going = True
		if command == 'd': #turn right
			keep = True	
		if command == 'w': #forward
			keep_for = True
		if command == 's': #top
		    keep_up = True
		if command == 'q':
			dc1 = 0
			dc2 = 0
			buff1 = buff2 = buff3 = buff4 = 0
			right()
			left()
			forward()
		if command == 'e':
			dc3 = 0
			buff5 = 0
			top()
		if command == 'y' and buff3 == 1:
			if buff5 ==1: #increase speed for goingup
				dc3 = dc3 + 10 
				if dc3 >= 90:
					dc3 = 90
				keep_up = True	
		if command == 'u' and buff3 == 1:
			if buff5 ==1: #decrease speed for goingup
				dc3 = dc3 - 10 
				if dc3 <= 5:
					dc3 = 10
				keep_up = True	
			 
		if command == 'h' and buff3 == 1:
			if buff4 ==1:#increase speed for forward
				dc2 = dc2 + 10 
				if dc2 >= 90:
					dc2 = 90
				dc1 = dc1 + 10 
				if dc1 >= 90:
					dc1 = 90
				keep_for = True	
			if buff1 ==1: #increase speed for left
				dc1 = dc1 + 10 
				if dc1 >= 90:
					dc1 = 90
				keep_going = True
				
			if buff2 ==1: #increase speed for right
				dc2 = dc2 + 10 
				if dc2 >= 90:
					dc2 = 90
				keep = True
		if command == 'j' and buff3 == 1:
			if buff4 ==1:#decrease speed for forward
				dc1 = dc1 - 10
				if dc1 <= 5:
					dc1 = 10
				dc2 = dc2 - 10 
				if dc2 <= 5:
					dc2 = 10
				keep_for = True		
			if buff1 ==1: #decrease speed for left
				dc1 = dc1 - 10
				if dc1 <= 5:
					dc1 = 10
				keep_going = True	
			if buff2 ==1: #decrease speed for right
				dc2 = dc2 - 10 
				if dc2 <= 5:
					dc2 = 10
				keep = True					
		if command == 'z':
			break
	
		while keep_going: #left
			if buff1 == 0:
				dc1 = 50
				buff3 = 1
			print 'left'
			left()
			buff1 = 1
			buff4 = 0
			buff2 = 0
			keep_going =False
				
		while keep: #right
			if buff2 == 0:
				dc2 = 50
				buff3 = 1
			print 'right'
			right()
			buff1 = 0
			buff4 = 0
			buff2 = 1
			keep = False
		while keep_for: #forward
			if buff4 == 0:
				dc1=dc2=50
				buff3 = 1
			print 'forward'
			forward()
			buff4 = 1
			buff1 = buff2 = 0
			keep_for = False
		while keep_up: #going up
			if buff5 == 0:
				dc3=50
				buff3 = 1
			print 'going up'
			top()
			buff5 = 1
			keep_up = False
		   
		 
		    
		   
		    
except KeyboardInterrupt:
	print("Ctl C pressed")

p.stop()
pwm.stop()
pto.stop()	
GPIO.cleanup()
