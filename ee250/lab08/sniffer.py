import paho.mqtt.client as mqtt
import time

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
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger1_dist = ranger1_dist[-MAX_LIST_LENGTH:]

def ranger2_callback(client, userdata, msg):
    global ranger2_dist
    ranger2_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
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
MAX_BUF_LEN = 10
ranger1_movAvg = []
ranger2_movAvg = []

def smoother1():
    global ranger1_movAvg
    tot = 0
    for val in ranger1_dist[-MAX_BUF_LEN:]:
        tot += int(val)
    avg = tot/MAX_BUF_LEN

    ranger1_movAvg.append(avg)

    #truncate list to only have the last MAX_BUF_LEN values
    ranger1_movAvg = ranger1_movAvg[-MAX_BUF_LEN:]

def smoother2():
    global ranger2_movAvg
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
# differences between each value (so for 20 movAvg values, we get 10 delta values)
# may change this and have function only return the two transient deltas
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

def stateMachine():
    # buffers for sensor error
    distance_buf = 10
    # grab last elements and cast to integers
    dump_list = (ranger1_deltas[-1:] + ranger2_deltas[-1:] + 
                ranger1_movAvg[-1:] + ranger2_movAvg[-1:])
    delta1 = int(dump_list[0])
    delta2 = int(dump_list[1])
    ranger1 = int(dump_list[2])
    ranger2 = int(dump_list[3])
    
    #STILL CONDITION
    if ((delta1 is 0) and (delta2 is 0)):
        # IF STILL AND LEFT
        if(ranger2 > ranger1 + distance_buf):
            print("Motion: STILL, Position: LEFT")
        # IF STILL AND RIGHT
        elif(ranger2 + distance_buf < ranger1):
            print("Motion: STILL, Position: LEFT")
        else:
            print("Motion: STILL, Position: MIDDLE")
    # elif((delta1 is 0) and (delta2 is 0)):


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

        # print("ranger1: " + str(ranger1_dist[-1:]) + ", ranger2: " + 
            # str(ranger2_dist[-1:])) 

        # build moving average lists

        print("ranger1: " + str(ranger1_dist[-1:]) + ", ranger2: " + 
            str(ranger2_dist[-1:])) 
        
        time.sleep(0.2)