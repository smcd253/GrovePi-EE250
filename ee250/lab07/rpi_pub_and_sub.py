"""EE 250L Lab 07 Skeleton Code

Run rpi_pub_and_sub.py on your Raspberry Pi."""

import paho.mqtt.client as mqtt
import time

import grovepi
from grovepi import *
from grove_rgb_lcd import *

# define grovepi vars
ultrasonic_ranger = 4
LED = 3
button = 2
pinMode(ultrasonic_ranger, "OUTPUT")
pinMode(LED, "OUTPUT")
pinMode(button,"INPUT")

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    client.subscribe("anrg-pi9/defaultCallback")
    client.subscribe("anrg-pi9/ultrasonic")
    client.message_callback_add("anrg-pi9/ultrasonic", ultrasonic)
    client.subscribe("anrg-pi9/led")
    client.message_callback_add("anrg-pi9/led", led)
    client.subscribe("anrg-pi9/button")
    client.message_callback_add("anrg-pi9/button", button)
    client.subscribe("anrg-pi9/lcd")
    client.message_callback_add("anrg-pi9/lcd", lcd)

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def ultrasonic(client, userdata, message):
    #the third argument is 'message' here unlike 'msg' in on_message 
    print("ultrasonic: " + message.topic + " " + "\"" + 
        str(message.payload, "utf-8") + "\"")

#Custom callbacks need to be structured with three args like on_message()
def led(client, userdata, message):
    #the third argument is 'message' here unlike 'msg' in on_message 
    data = str(message.payload, "utf-8")
    if (data == "LED_ON"):
        digitalWrite(LED, 1)
    elif (data == "LED_OFF"):
        digitalWrite(LED, 0)

def button(client, userdata, message):
    #do nothing?

def lcd(client, userdata, message):
    data = str(message.payload, "utf-8")
    print("From VM: " + data)
    setRGB(64,0,128)   # parse our list into the color settings
    setText("From VM: " + data) # update the RGB LCD display

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    while True:
        ################ ULTRASONIC RANGER ###############
        try:
            # Read distance value from Ultrasonic
            dist = grovepi.ultrasonicRead(ultrasonic_ranger)
            data = str(dist)

        except TypeError:
            data = "TypeError"
        except IOError:
            data = "IOError"

        client.publish("anrg-pi9/ultrasonic", data)

        ################ BUTTON ###############
        try:
            button_status = digitalRead(button)	#Read the Button status
            if button_status:
                client.publish("anrg-pi9/button", "Button Pressed!")									
        except (IOError,TypeError) as e:
            client.publish("anrg-pi9/button", "Button ERROR")


        time.sleep(1)
            

