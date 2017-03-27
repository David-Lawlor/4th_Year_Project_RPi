# reference
# http://www.raspberry-projects.com/pi/programming-in-python/i2c-programming-in-python/using-the-i2c-interface-2

import smbus
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import os
import RPi.GPIO as GPIO
from uuid import getnode
import hashlib
import json

GPIO.setmode(GPIO.BCM)

# smbus is a subset of i2c used for writing to an i2c device
# i2c is used for connecting low power peripherals to processors
# 0 for raspberry pi 1 otherwise 1
bus = smbus.SMBus(1)

# PCF8591 address 'sudo i2cdetect -y 1'
address = 0x48

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

previous_reading = 0
while True:
    try:
        # dummy write to device
        bus.write_byte(address, 0x40)
        lux = bus.read_byte(address)  # dummy read needed

        # a photoresistors resistance goes down as the amount of light falling
        # on the surface increases
        # 0 lux = no light
        # min resistance reading = 0; max resistance reading = 160;
        # To correct this the max value minus the reading is used to inverse the scale
        lux = 160 - bus.read_byte(address)

        # bright room is ~100-120 lux so the 0-160 range is will be
        # mapped to the 1-120 range
        lux = (lux * 120) / 160

        if lux != previous_reading:
            light_data = {
		'Partition_Key': hashlib.sha1(hex(getnode())[2:-1]).hexdigest() + 'light',
                'Timestamp': time.strftime("%d%m%Y", time.gmtime())+time.strftime("%H%M%S"),
                'UserID': hashlib.sha1(hex(getnode())[2:-1]).hexdigest(),
                'Date': time.strftime("%d-%m-%Y", time.gmtime()),
                'Device_Type': 'Light Sensor',
                'Current_Temperature': lux,
                'Time': time.strftime("%H:%M:%S"),
                'Location': 'Room 1'
            }
            print 'lux = %.2f' % lux
            myAWSIoTMQTTClient.publish("/things/Raspberry_Pi_2/light/room1",
                                       json.dumps(light_data), 1)

        # wait 5 seconds before checking again
        previous_reading = lux
        time.sleep(600)
    except KeyboardInterrupt:
        GPIO.cleanup()

