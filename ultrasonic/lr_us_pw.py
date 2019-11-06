import serial
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(15,GPIO.IN) # PW input pin
GPIO.setup(24,GPIO.IN) # PW input pin
GPIO.setup(23,GPIO.OUT) # Measurement trig pin

up_time15 = 0
dist15 = 0
rising15 = False

up_time24 = 0
dist24 = 0
rising24 = False

pwm = GPIO.PWM(23, 1)
	
def cb_15(channel):
	global up_time15, dist15, rising15
	if GPIO.input(15) and not rising15:
		# Rising edge
		up_time15 = time.time()
		rising15 = True
	elif rising15:
		# Falling edge
		pulse_time15 = time.time() - up_time15
		dist15 = pulse_time15 / 0.000147 # 147 us / in
		print("Distance 15: {} in".format(dist15))
		rising15 = False
	
def cb_24(channel):
	global up_time24, dist24, rising24
	if GPIO.input(24) and not rising24:
		# Rising edge
		up_time24 = time.time()
		rising24 = True
	elif rising24:
		# Falling edge
		pulse_time24 = time.time() - up_time24
		dist24 = pulse_time24 / 0.000147 # 147 us / in
		print("Distance 24: {} in".format(dist24))
		rising24 = False
	
GPIO.add_event_detect(15, GPIO.BOTH, callback=cb_15)
GPIO.add_event_detect(24, GPIO.BOTH, callback=cb_24)


try:
	
	pwm.start(0.1) # trig pulse
	
	while True:
		pass
		
except KeyboardInterrupt:
	pass
	
GPIO.cleanup()
