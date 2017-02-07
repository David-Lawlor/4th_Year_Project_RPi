from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO
import logging
import json
import os
import time

relay_states = {
    "relay1": "OFF",
    "relay2": "OFF",
    "relay3": "OFF",
    "relay4": "OFF",
}

def report_initial_states():
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

    myAWSIoTMQTTClient.publish("$aws/things/Raspberry_Pi_2/shadow/update",
                                     '{"state":{"reported":' + json.dumps(relay_states) + '}}', 1)



class shadowCallbackContainer:



    GPIO.setmode(GPIO.BCM)
    
    relay_pins = {
        "relay1": 12,
        "relay2": 16,
        "relay3": 20,
        "relay4": 21,
    }

    # loop through pins and set mode and state to 'high'

    for pin in relay_pins:
        GPIO.setup(relay_pins[pin], GPIO.OUT)
        GPIO.output(relay_pins[pin], GPIO.HIGH)

    SleepTimeL = 2

    def __init__(self, deviceShadowInstance):
        self.deviceShadowInstance = deviceShadowInstance

    def change_relay_state(self, relay_state, relay_pin):
        try:
            print "the relay state is ", relay_state
            print "the relay pin is ", relay_pin
            if relay_state == 'ON':
                GPIO.output(relay_pin, GPIO.LOW)
            else:
                GPIO.output(relay_pin, GPIO.HIGH)

        # End program cleanly with keyboard
        except KeyboardInterrupt:
            print "  Quit"

            # Reset GPIO settings
            GPIO.cleanup()

    # Custom Shadow callback
    def customShadowCallback_Delta(self, payload, responseStatus, token):
        # payload is a JSON string ready to be parsed using json.loads(...)
        # in both Py2.x and Py3.x
        print("Received a delta message:")

        # PA
        payloadDict = json.loads(payload)
        print payloadDict
        deltaMessage = json.dumps(payloadDict["state"])
        print(deltaMessage)

        # for each of the relays in the delta message change the state
        for relay in payloadDict["state"]:
            self.change_relay_state(payloadDict["state"][relay], self.relay_pins[relay])

        print("Request to update the reported state...")
        newPayload = '{"state":{"reported":' + deltaMessage + '}}'
        self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)
        print("Sent.")


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

# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None

myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient("ThingShadowEcho")
myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a deviceShadow with persistent subscription
Raspberry_Pi_2_shadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("Raspberry_Pi_2", True)
shadowCallbackContainer_Bot = shadowCallbackContainer(Raspberry_Pi_2_shadow)

# Listen on deltas
Raspberry_Pi_2_shadow.shadowRegisterDeltaCallback(shadowCallbackContainer_Bot.customShadowCallback_Delta)

report_initial_states()

# Loop forever
while True:
    pass

