import paho.mqtt.client as mqtt
import time
import requests
import json
from datetime import datetime
import time

#!!!!!!!!!!!!!!!!NOTE!!!!!!!!!!!!!!!!!!#
#THIS SCRIPT CANNOT BE RUN UNLESS flask_server.py IS RUNNING ON ANOTHER TERMINAL

############################## HTTP #################################
# This header sets the HTTP request's mimetype to `application/json`. This
# means the payload of the HTTP message will be formatted as a json ojbect
hdr = {
    'Content-Type': 'application/json',
    'Authorization': None #not using HTTP secure
}



# MQTT variables
broker_hostname = "eclipse.usc.edu"
broker_port = 11000
ultrasonic_ranger1_topic = "ultrasonic_ranger1"
ultrasonic_ranger2_topic = "ultrasonic_ranger2"

# Lists holding the ultrasonic ranger sensor distance readings. Change the 
# value of MAX_LIST_LENGTH depending on how many distance samples you would 
# like to keep at any point in time.
MAX_LIST_LENGTH = 100
ranger1_dist = []
ranger2_dist = []

def ranger1_callback(client, userdata, msg):
    global ranger1_dist
    ranger1_dist.append(int(msg.payload))
    ranger1_dist = ranger1_dist[-MAX_LIST_LENGTH:]

def ranger2_callback(client, userdata, msg):
    global ranger2_dist
    ranger2_dist.append(int(msg.payload))
    ranger2_dist = ranger2_dist[-MAX_LIST_LENGTH:]

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(ultrasonic_ranger1_topic)
    client.message_callback_add(ultrasonic_ranger1_topic, ranger1_callback)
    client.subscribe(ultrasonic_ranger2_topic)
    client.message_callback_add(ultrasonic_ranger2_topic, ranger2_callback)

# The callback for when a PUBLISH message is received from the server.
# This should not be called.
def on_message(client, userdata, msg): 
    print(msg.topic + " " + str(msg.payload))


########################## SIGNAL PROCESSING ############################
MAX_BUF_LEN = 10 # the number of values sitting in the moving average 
                 # and delta buffers
ranger1_movAvg = []
ranger2_movAvg = []

# builds moving average buffers for each ranger
# adds up total of last MAX_BUF_LEN values in distance buffer,
# divides the total by MAX_BUF_LEN to find the average
# and appends is value to the moving average buffer
def smoother():

    global ranger1_movAvg
    global ranger2_movAvg
    tot = 0
    for val in ranger1_dist[-MAX_BUF_LEN:]:
        tot += int(val)
    avg = tot/MAX_BUF_LEN

    ranger1_movAvg.append(avg)

    #truncate list to only have the last MAX_BUF_LEN values
    ranger1_movAvg = ranger1_movAvg[-MAX_BUF_LEN:]

    tot = 0
    for val in ranger2_dist[-MAX_BUF_LEN:]:
        tot += int(val)
    avg = tot/MAX_BUF_LEN
    
    ranger2_movAvg.append(avg)

    #truncate list to only have the last MAX_BUF_LEN values
    ranger2_movAvg = ranger2_movAvg[-MAX_BUF_LEN:]
    

ranger1_deltas = []
ranger2_deltas = []

# takes last two values in each moving average array and creates an array of 
# differences between each value 
# (so for example: 20 movAvg values, we get 10 delta values)
def delta():
    global ranger1_deltas
    global ranger2_deltas

    deltas_1 = ranger1_movAvg[-2:]
    delta1 = int(deltas_1[0]) - int(deltas_1[-1])

    deltas_2 = ranger2_movAvg[-2:]
    delta2 = int(deltas_2[0]) - int(deltas_2[-1])

    ranger1_deltas.append(delta1)
    ranger1_deltas = ranger1_deltas[-MAX_BUF_LEN:]
    ranger2_deltas.append(delta2)
    ranger2_deltas = ranger2_deltas[-MAX_BUF_LEN:]

# stateMachine() is where the moving average and delta bufffers are analized
# to determine the behavior of the subject
def stateMachine():
    #################################### HTTP ################################3
    # payload definitions for all motion options
    # this must be defined each time stateMachine() is called
    # so we can grab the correct timestamp
    pload_mvRight = {
        'time': str(datetime.now()),
        'event': "Moving - Right"
    }
    pload_mvLeft = {
        'time': str(datetime.now()),
        'event': "Moving - Left"
    }
    pload_stRight = {
        'time': str(datetime.now()),
        'event': "Still - Right"
    }
    pload_stLeft = {
        'time': str(datetime.now()),
        'event': "Still - Left"
    }
    pload_stMiddle = {
        'time': str(datetime.now()),
        'event': "Still - Middle"
    }
    pload_noBody = {
        'time': str(datetime.now()),
        'event': "No Body Present"
    }

    # buffer for sensor error
    distance_buf = 20
    # grab last elements and cast to integers
    # we put the values into dump_list because grabbing value
    # list[-1:] returns a list, and cannot be cast to an integer
    dump_list = (ranger1_deltas[-1:] + ranger2_deltas[-1:] + 
                ranger1_movAvg[-1:] + ranger2_movAvg[-1:])
    delta1 = int(dump_list[0])
    delta2 = int(dump_list[1])
    ranger1 = int(dump_list[2])
    ranger2 = int(dump_list[3])
    
    ############################ LOGIC ##############################
    # here we will decide if a person is moving left or right, standing
    # in the left, right, or middle sections of the test area
    # or is not present in the test area at all
    # presence is determined by whether or not the user is within 
    # the max_dist defined below
    max_dist = 150
    #STILL CONDITION
    if ((ranger1 > max_dist) and (ranger2 > max_dist)):
        print("No Body Present")
        response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                 data = json.dumps(pload_noBody))
    elif ((delta1 is 0) and (delta2 is 0)):
        # IF STILL AND LEFT
        if(ranger2 > ranger1 + distance_buf):
            print("Motion: STILL, Position: LEFT")
            response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                 data = json.dumps(pload_stLeft))
        # IF STILL AND RIGHT
        elif(ranger2 + distance_buf < ranger1):
            print("Motion: STILL, Position: RIGHT")
            response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                 data = json.dumps(pload_stRight))
        else:
            print("Motion: STILL, Position: MIDDLE")
            response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                 data = json.dumps(pload_stMiddle))
            
    # MOVING CONDITION
    else:
        # IF MOVING RIGHT
        if ((delta1 > 0) and (delta2 < 0)):
            print("Motion: MOVING, Direction: LEFT")
            response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                 data = json.dumps(pload_mvLeft))
        # IF MOVING LEFT
        elif ((delta1 < 0) and (delta2 > 0)):
            print("Motion: MOVING, Direction: RIGHT")
            response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                 data = json.dumps(pload_mvRight))

#!!!!!!!!!!!!!!!!NOTE!!!!!!!!!!!!!!!!!!#
#THIS SCRIPT CANNOT BE RUN UNLESS flask_server.py IS RUNNING ON ANOTHER TERMINAL

if __name__ == '__main__':
    # Connect to broker and start loop    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_hostname, broker_port, 60)
    client.loop_start()

    # moving average buffers
    ranger1_movAvg = []
    ranger2_movAvg = []



    while True:
        """ You have two lists, ranger1_dist and ranger2_dist, which hold a window
        of the past MAX_LIST_LENGTH samples published by ultrasonic ranger 1
        and 2, respectively. The signals are published roughly at intervals of
        200ms, or 5 samples/second (5 Hz). The values published are the 
        distances in centimeters to the closest object. Expect values between 
        0 and 512. However, these rangers do not detect people well beyond 
        ~125cm. """

        # calculate moving average
        smoother()
        
        # calculate velocity
        delta()

        # perform logic to determin subject behavior
        stateMachine()
     
        time.sleep(0.2)