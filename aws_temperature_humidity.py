'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import os
import RPi.GPIO as GPIO
import Adafruit_DHT
from uuid import getnode
import hashlib
import json

# sensor type 11 Adafruit_DHT.DHT11
sensor_type = 11

# The GPIO pin that the sensor is connected to
GPIO_pin = 17


# Read in command-line parameters
useWebsocket = False
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
        # Try to grab a sensor reading.  Use the read_retry method which will
        # retry up to 15 times to get a sensor reading (waiting 2 seconds between
        # each retry).
        humidity, temperature = Adafruit_DHT.read_retry(sensor_type, GPIO_pin)
        if humidity is not None and temperature is not None:

            temperatureData = {
                'UserID': hashlib.sha1(hex(getnode())[2:-1]).hexdigest(),
                'Date': time.strftime("%d-%m-%Y", time.gmtime()),
                'Device_Type': 'Temperature Sensor',
                'Current_Temperature': 'Temp={0:0.1f}*'.format(temperature),
                'Time': time.strftime("%H:%M:%S"),
                'Location': 'Room 2'
            }

            humidityData = {
                'UserID': hashlib.sha1(hex(getnode())[2:-1]).hexdigest(),
                'Date': time.strftime("%d-%m-%Y", time.gmtime()),
                'Device_Type': 'Humidity Sensor',
                'Current_Humidity': 'Humidity={1:0.1f}%'.format(humidity),
                'Time': time.strftime("%H:%M:%S"),
                'Location': 'Room 2'
            }

            myAWSIoTMQTTClient.publish("/things/Raspberry_Pi_2/temperature/room2",
                                        json.dumps(temperatureData), 1)

            myAWSIoTMQTTClient.publish("/things/Raspberry_Pi_2/humidity/room2",
                                        json.dumps(humidityData), 1)

        # wait 5 seconds before checking again
        time.sleep(60)
    except KeyboardInterrupt:
        GPIO.cleanup()
