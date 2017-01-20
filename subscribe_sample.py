from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import RPi.GPIO as GPIO
import logging
import json
import os
import time



class shadowCallbackContainer:
    def __init__(self, deviceShadowInstance):
        self.deviceShadowInstance = deviceShadowInstance

    def changeRelayState(self, state_relay):
        GPIO.setmode(GPIO.BCM)
        # init list with pin numbers

        pinList = [12, 16, 20, 21]

        # loop through pins and set mode and state to 'high'

        for i in pinList:
            GPIO.setup(i, GPIO.OUT)
            GPIO.output(i, GPIO.HIGH)

        SleepTimeL = 2
        try:
            GPIO.output(12, GPIO.LOW)
            print "ONE"
            time.sleep(SleepTimeL)
            GPIO.output(16, GPIO.LOW)
            print "TWO"
            time.sleep(SleepTimeL)
            GPIO.output(20, GPIO.LOW)
            print "THREE"
            time.sleep(SleepTimeL)
            GPIO.output(21, GPIO.LOW)
            print "FOUR"
            time.sleep(SleepTimeL)
            GPIO.cleanup()
            print "Good bye!"

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
        payloadDict = json.loads(payload)
        print payloadDict
        deltaMessage = json.dumps(payloadDict["state"])
        print(deltaMessage)
        self.changeRelayState(deltaMessage)
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

# Loop forever
while True:
    pass
