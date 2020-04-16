#!/usr/bin/python

import time
import VL53L0X
import RPi.GPIO as GPIO
import random

shutdown_pins = [23,24,25]
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Setup GPIO for shutdown pins on each VL53L0X
for pin in shutdown_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Keep all low for 500 ms or so to make sure they reset
time.sleep(0.5)

# Create one object per VL53L0X passing the address to give to
# each.
tof_objects = {}
tof_objects[shutdown_pins[0]] = VL53L0X.VL53L0X(address=0x2A)
tof_objects[shutdown_pins[1]] = VL53L0X.VL53L0X(address=0x2C)
tof_objects[shutdown_pins[2]] = VL53L0X.VL53L0X(address=0x2E)

# Set shutdown pin high for VL53L0X then call to start ranging
for pin in shutdown_pins:
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.50)
    tof_objects[pin].start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

distances = [0,0,0]

while(True):                
    for i in range(3):
        distance = tof_objects[shutdown_pins[i]].get_distance()
        while (distance == -1):
            GPIO.output(shutdown_pins[i], GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(shutdown_pins[i], GPIO.HIGH)
            time.sleep(0.1)
            tof_objects[shutdown_pins[i]].start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
        distances[i] = distance
    print(distances)