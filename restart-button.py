#!/bin/python 
import RPi.GPIO as GPIO  
import time  
import os  
GPIO.setmode(GPIO.BCM)  
GPIO.setwarnings(False)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
def Restart(channel):
   os.system("sudo shutdown -r now")
GPIO.add_event_detect(10,GPIO.RISING,callback=Restart, bouncetime = 2000)
while 1:  
   time.sleep(1)