# Raspberry Pi Thermal Cam

## Demo

See demo below, note restart button and color changing LED when heat is detected.

![Demo Of Thermal Cam](https://github.com/jacobscarter/raspberry-pi-thermal-cam/blob/master/demo-gif.gif?raw=true)

## Using ADAFRUIT AMG8833 IR THERMAL CAMERA [Amazon Link](https://www.amazon.com/gp/product/B07D7LXXWR/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&psc=1)
* Install for Raspberry Pi: https://learn.adafruit.com/adafruit-amg8833-8x8-thermal-camera-sensor/raspberry-pi-thermal-camera
* There are a lot of deprecated packages and outdated tutorials. I followed the above tutorial with the caveat that I used this link to ensure all dependencies were installed: https://learn.adafruit.com/circuitpython-on-raspberrypi-linux
* Must be on Python 3. I found it easiest to set this as your default: https://linuxconfig.org/how-to-change-from-default-to-alternative-python-version-on-debian-linux
* Also ran into some issues around `root` versus `pi` user. Ended up running all code as `pi` not `root`
* Ran into issues install SciPy, ended up using this link and ensuring I was not root while installing: https://www.raspberrypi.org/forums/viewtopic.php?t=112308

## Customizations
* Added a Reset button to my Pi, code can be seen in restart-button.py
* Initial restart code on startup using `/etc/rc.local`, you can see that method and others here: https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/
* Added two LEDs (green and red). Green light is on by default, then when enough "hot pixels" enter the frame the green light turns off and red light turns on. That can be seen with the "hotPixels" variable
```python
    hotPixels=0
    for ix, row in enumerate(BICUBIC):
        x_console = 2
        for jx, pixel in enumerate(row):
            color_index = 0
            if pixel > 300:
                hotPixels = hotPixels+1
            if COLOR_RANGE != 0:
                color_index = int(round((pixel - MINPIXEL) / COLOR_RANGE))
            if color_index < 0:
                color_index = 0
            if color_index > len(CONSOLE_COLORS) - 1:
                color_index = len(CONSOLE_COLORS) - 1
            print_there(x_console, Y_CONSOLE * 2 - 2, "  ", CONSOLE_COLORS[color_index])
            if pixel > MAXPIXEL:
                MAXPIXEL = pixel
            if pixel < MINPIXEL:
                MINPIXEL = pixel
            x_console += 1
        Y_CONSOLE += 1
    sys.stdout.flush()
    HEAT_RANGE = MAXPIXEL - MINPIXEL
    COLOR_RANGE = HEAT_RANGE / len(CONSOLE_COLORS)
    if hotPixels > 10:
        GPIO.output(18,GPIO.HIGH)
        GPIO.output(25,GPIO.LOW)
    else:
        GPIO.output(18,GPIO.LOW)
        GPIO.output(25,GPIO.HIGH)
```
* There are 3 thermal cam code files.
  * 1 will open a new window with a video feed to show you thermal readings
  * The second will leverage your console to output a visual feed (this one visually looks best)
  * The third doesnt not have an output, if you want to start the code on reboot of the Pi then you need to use this option, also required for background or headless execution
* Becuase the python code to initiate the thermal cam logic must be run from `pi` and not `root` (This may not be the case for you if you install the dependencies more cleanly that I did) I could not use `/etc/rc.local` to run the python script on startup because I need the `pi` user to run it.
For this reason I used `crontab -e` with an @reboot command to ensure the code was ran by the correct user on startup.
```bash
@reboot /bin/bash /home/pi/thermal-cam/startup.sh
```
* `startup.sh` is simply:
```bash
#!/bin/bash

python3 /home/pi/thermal-cam/thermal-cam-bare.py >> /home/pi/thermal-cam/cam-logs.txt
```
