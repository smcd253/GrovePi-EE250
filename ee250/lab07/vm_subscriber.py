"""EE 250L Lab 07 Skeleton Code

Run vm_subscriber.py in a separate terminal on your VM."""

import paho.mqtt.client as mqtt
import time


def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to the ultrasonic ranger topic here
    client.subscribe("anrg-pi9/defaultCallback")
    client.subscribe("anrg-pi9/ultrasonic")
    client.message_callback_add("anrg-pi9/ultrasonic", ultrasonic)

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

#Custom callbacks need to be structured with three args like on_message()
def ultrasonic(client, userdata, message):
    #the third argument is 'message' here unlike 'msg' in on_message 
    print("ultrasonic: " + message.topic + " " + "\"" + 
        str(message.payload, "utf-8") + "\"")
    print("ultrasonic: message.payload is of type " + 
          str(type(message.payload)))

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    while True:
        time.sleep(1)
            

