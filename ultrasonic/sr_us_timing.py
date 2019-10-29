import serial
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class sr_us:
	
	def __init__(self, trig_pin, echo_pin, timeout=1.):
		
		GPIO.setup(trig_pin,GPIO.OUT) # Trig
		GPIO.setup(echo_pin,GPIO.IN)  # Echo
		
		self.trig = trig_pin
		self.echo = echo_pin
		self.timeout = timeout
	
	def dist(self):
		
		# Trigger pulse
		GPIO.output(self.trig,GPIO.HIGH)
		time.sleep(0.00001)
		GPIO.output(self.trig,GPIO.LOW)
		
		start_time = time.time()		
		
		# Wait for start return pulse
		while not GPIO.input(self.echo):
			if (time.time() - start_time) > self.timeout:
				raise RuntimeError("US timed out low")
				
		echo_time = time.time()
		
		# Wait for end of return pulse
		while GPIO.input(self.echo):
			if (time.time() - echo_time) > self.timeout:
				raise RuntimeError("US timed out high")
		
		# Calculate dist from time echo pin is high
		return (time.time() - echo_time) * 17000
		
try:
	us1 = sr_us(27,17)

	for i in range(10):
		print(us1.dist())
except RuntimeError as e:
	print(e)
except KeyboardInterrupt:
	pass
	
GPIO.cleanup()	
