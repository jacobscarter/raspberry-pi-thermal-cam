"""This example is for Raspberry Pi (Linux) only!
   It will not work on microcontrollers running CircuitPython!"""

import os
import math
import time

import busio
import board

import numpy as np
import pygame
from scipy.interpolate import griddata

from colour import Color

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
    print("Preparing for shutdown")
    GPIO.output(18,GPIO.LOW)
    GPIO.output(25,GPIO.LOW)
    sys.exit(1)

    # restore the exit gracefully handler here    
    signal.signal(signal.SIGINT, exit_gracefully)
original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)


i2c_bus = busio.I2C(board.SCL, board.SDA)

# low range of the sensor (this will be blue on the screen)
MINTEMP = 26.0

# high range of the sensor (this will be red on the screen)
MAXTEMP = 32.0

# how many color values we can have
COLORDEPTH = 1024

os.putenv("SDL_FBDEV", "/dev/fb1")
pygame.init()

# initialize the sensor
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# pylint: disable=invalid-slice-index
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
# pylint: enable=invalid-slice-index

# sensor is an 8x8 grid so lets do a square
height = 240
width = 240

# the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

# create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

displayPixelWidth = width / 30
displayPixelHeight = height / 30

lcd = pygame.display.set_mode((width, height))

lcd.fill((255, 0, 0))

pygame.display.update()
pygame.mouse.set_visible(False)

lcd.fill((0, 0, 0))
pygame.display.update()

# some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


# let the sensor initialize
time.sleep(0.1)

while True:

    # read the pixels
    pixels = []
    for row in sensor.pixels:
        pixels = pixels + row
    pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]

    # perform interpolation
    bicubic = griddata(points, pixels, (grid_x, grid_y), method="cubic")

    hotPixels=0
    # draw everything
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            if pixel > 300:
                hotPixels = hotPixels+1
            pygame.draw.rect(
                lcd,
                colors[constrain(int(pixel), 0, COLORDEPTH - 1)],
                (
                    displayPixelHeight * ix,
                    displayPixelWidth * jx,
                    displayPixelHeight,
                    displayPixelWidth,
                ),
            )

    if hotPixels > 10:
        GPIO.output(18,GPIO.HIGH)
        GPIO.output(25,GPIO.LOW)
    else:
        GPIO.output(18,GPIO.LOW)
        GPIO.output(25,GPIO.HIGH)

    pygame.display.update()