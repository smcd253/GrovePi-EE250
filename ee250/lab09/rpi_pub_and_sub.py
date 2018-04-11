"""EE 250L Lab 07 Skeleton Code

Run rpi_pub_and_sub.py on your Raspberry Pi."""

import paho.mqtt.client as mqtt
import time

import grovepi
from grovepi import *
from grove_rgb_lcd import *
from grove_dht import Dht

# define grovepi vars
dht_pin = 4
LED = 3

#dht
dht_sensor = Dht(dht_pin)
dht_sensor.start() #start collecting dht data

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    client.subscribe("anrg-pi9/defaultCallback")
    client.subscribe("anrg-pi9/temperature")
    client.subscribe("anrg-pi9/humidity")
    client.subscribe("anrg-pi9/led")
    client.message_callback_add("anrg-pi9/led", led)
    client.subscribe("anrg-pi9/lcd")
    client.message_callback_add("anrg-pi9/lcd", lcd)

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

#Custom callbacks need to be structured with three args like on_message()
def led(client, userdata, message):
    #the third argument is 'message' here unlike 'msg' in on_message 
    data = str(message.payload, "utf-8")
    if ((data == "TOGGLE") and digitalRead(LED) == 0): #if receive message and LED is off
        digitalWrite(LED, 1) #turn LED on
    elif ((data == "TOGGLE") and digitalRead(LED) == 1): #if receive message and LED is on
        digitalWrite(LED, 0) #turn LED off

def lcd(client, userdata, message):
    data = str(message.payload, "utf-8")
    print("From App: " + data)
    setRGB(64,0,128)   # parse our list into the color settings
    setText("From App: " + data) # update the RGB LCD display

if __name__ == '__main__':
    pinMode(dht_pin, "INPUT")
    pinMode(LED, "OUTPUT")
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    while True:
        ################ DHT ###############
        try:
            temp, hum = dht_sensor.feedMe() # try to read values
            client.publish("anrg-pi9/temperature", temp)
            client.publish("anrg-pi9/humidity", hum)
        except KeyboardInterrupt:
            dht_sensor.stop() # stop gathering data
        time.sleep(1)
            

