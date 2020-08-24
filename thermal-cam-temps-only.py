import time
import busio
import board
import adafruit_amg88xx

import signal
import sys

#logic for LED light
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)

#logic to handle graceful shutdown
def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)
    timestamp = time.strftime("%Y-%m-%d %X")
    print(timestamp, "Preparing for shutdown")
    GPIO.output(18,GPIO.LOW)
    GPIO.output(25,GPIO.LOW)
    sys.exit(1)

    # restore the exit gracefully handler here    
    signal.signal(signal.SIGINT, exit_gracefully)
original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)

i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)

while True:
    hotPixels=0
    for row in amg.pixels:
        for temp in row:
            if temp > 20:
                hotPixels = hotPixels+ 1
    if hotPixels > 1:
        GPIO.output(18,GPIO.HIGH)
        GPIO.output(25,GPIO.LOW)
    else:
        GPIO.output(18,GPIO.LOW)
        GPIO.output(25,GPIO.HIGH)
