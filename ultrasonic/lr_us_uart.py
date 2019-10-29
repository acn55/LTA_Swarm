import serial
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(18,GPIO.OUT) #drive high for reading
GPIO.output(18,GPIO.HIGH)

try:

	ser = serial.Serial("/dev/ttyS0", 9600)
	received_byte = "a"
	while True:
		
		print("Waiting for byte...\n")
		range_str = ""
		
		# Wait for R
		while not (received_byte == 'R'):
			print(received_byte)
			received_byte = ser.read()
		
		print("Got R\n")
		
		# Read until new line
		while not (received_byte == '\r'):
			received_byte = ser.read()
			range_str += received_byte
		
		print("Range = " + range_str)
		
except KeyboardInterrupt:
	GPIO.cleanup()
	
GPIO.cleanup()
