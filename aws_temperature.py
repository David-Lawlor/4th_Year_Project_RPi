from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import re
import os
import RPi.GPIO as GPIO
from uuid import getnode
import hashlib
import json


def read_file():
    # open the modprobe file
    temperature_file = open("/sys/bus/w1/devices/28-03165624a6ff/w1_slave")

    # read the text into a string
    text = temperature_file.read()

    # close the temperature file
    temperature_file.close()

    # return the parsed text
    return text

host = os.environ['host']

rootCAPath = os.environ['rootCAPath']

certificatePath = os.environ['certificatePath']

privateKeyPath = os.environ['privateKeyPath']

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient("")
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath,
                                        privateKeyPath,
                                        certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)

# Infinite offline Publish queueing
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)

# Draining: 2 Hz
myAWSIoTMQTTClient.configureDrainingFrequency(2)

# 10 sec
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)

# 5 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()

# Publish to the same topic in a loop forever
loopCount = 0
while True:
    try:
        read_file()

        # read the file to a string
        text1 = read_file()

        # compile regex (t={0 to 6 digits}
        text_re = re.compile("[t][=]\d{3,6}")

        # search the string
        found = text_re.search(text1)

        # if the string is found parse it to a float and change to decimal
        temperature = (float(found.group()[2:])) / 1000

        data = {
            'UserID': hashlib.sha1(hex(getnode())[2:-1]).hexdigest(),
            'Date': time.strftime("%d-%m-%Y", time.gmtime()),
            'Device_Type': 'Temperature Sensor',
            'Current_Temperature': '{0:0.1f}'.format(temperature),
            'Time': time.strftime("%H:%M:%S"),
            'Location': 'Room 1'
        }

        myAWSIoTMQTTClient.publish("/things/Raspberry_Pi_2/temperature/room1",
                                    json.dumps(data), 1)

        # wait 5 seconds before checking again
        time.sleep(10)
    except KeyboardInterrupt:
        GPIO.cleanup()
