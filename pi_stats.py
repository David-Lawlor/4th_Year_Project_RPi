from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import os
from uuid import getnode
import hashlib
import json
import socket

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
    # CPU

    # get the current cpu temp in celsius
    cpu_temperature = os.popen('/opt/vc/bin/vcgencmd measure_temp').read()
    # strip off the unneeded extra characters
    cpu_temperature = cpu_temperature[5:].strip('\n').strip('C').strip('\'')

    # get the cpu utilisation
    cpu_idle = os.popen('mpstat  | awk \'/all/ { print $NF }\'').readline()
    # convert the idle to utilisation
    cpu_utilisation = 100 - (float(cpu_idle))

    # RAM

    # total ram available in megabytes
    total_ram = os.popen('free  | awk \'/Mem/ { print $2 }\'').readline()
    # cast to int
    total_ram = int(total_ram)

    # amount of ram available in megabytes
    free_ram = os.popen('free  | awk \'/Mem/ { print $4 }\'').readline()
    # cast to int
    free_ram = int(free_ram)

    # Storage

    # get the total amount of storage available in megabytes
    total_storage = os.popen('df -B M --total  | awk \'/total/ {print $2}\'').readline()
    # strip off the unneeded characters and cast to float
    total_storage = float(total_storage.strip('\n').strip('M'))

    # get the unneeded storage
    free_storage = os.popen('df -B M --total  | awk \'/total/ {print $4}\'').readline()
    # strip off the unneeded characters and cast to float
    free_storage = float(free_storage.strip('\n').strip('M'))

    # get the used storage space
    used_storage = os.popen('df -B M --total  | awk \'/total/ {print $3}\'').readline()
    # strip off the unneeded characters and cast to float
    used_storage = float(used_storage.strip('\n').strip('M'))

    # Network Stats

    # get the default gateway
    gw = os.popen("ip -4 route show default").read().split()
    gateway = gw[2]

    # get ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    ip_address = s.getsockname()[0]

    # hostname
    hostname = socket.gethostname()

    piData = {
        'UserID': hashlib.sha1(hex(getnode())[2:-1]).hexdigest(),
        'CPU_Temperature': float(cpu_temperature),
        'CPU_Utilisation': float('{0:0.1f}'.format(cpu_utilisation)),
        'Total_RAM': total_ram,
        'Free_RAM': free_ram,
        'Total_Storage': total_storage,
        'Free_Storage': free_storage,
        'Used_Storage': used_storage,
        'Default_Gateway': gateway,
        'IP_Address': ip_address,
        'Hostname': hostname
    }
    print piData

    myAWSIoTMQTTClient.publish("/things/Raspberry_Pi_2/device_stats", json.dumps(piData), 1)

    # wait 600 seconds before checking again
    time.sleep(600)

