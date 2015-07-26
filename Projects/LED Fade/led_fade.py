# Adjust LED brightness by rotating Potentiometer

# GrovePi + Rotary Angle Sensor (Potentiometer) + LED
# http://www.seeedstudio.com/wiki/Grove_-_Rotary_Angle_Sensor
# http://www.seeedstudio.com/wiki/Grove_-_LED_Socket_Kit

'''
## License
 GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
 Copyright (C) 2015  Dexter Industries

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
'''

import time
import grovepi

# Connect the Rotary Angle Sensor to analog port A2
potentiometer = 2

# Connect the LED to digital port D5
led = 5

grovepi.pinMode(led,"OUTPUT")
time.sleep(1)
i = 0

while True:
    try:
        # Read resistance from Potentiometer
        i = grovepi.analogRead(potentiometer)
        print i

        # Send PWM signal to LED
        grovepi.analogWrite(led,i/4)

    except IOError:
        print "Error"
