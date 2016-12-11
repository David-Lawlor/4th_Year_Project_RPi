import re
import time
import RPi.GPIO as GPIO


def read_file():
    # open the modprobe file
    temperature_file = open("/sys/bus/w1/devices/28-03165624a6ff/w1_slave")

    # read the text into a string
    text = temperature_file.read()

    # close the temperature file
    temperature_file.close()

    # return the parsed text
    return text


def loop():
    while True:
        # read the file to a string
        text1 = read_file()

        # compile regex (t={0 to 6 digits}
        text_re = re.compile("[t][=]\d{3,6}")

        # search the string
        found = text_re.search(text1)

        # if the string is found parse it to a float and change to decimal
        temperature = (float(found.group()[2:])) / 1000
        print (temperature)

        # wait 5 seconds before checking again
        time.sleep(5)


try:
    read_file()
    loop()
except KeyboardInterrupt:
    GPIO.cleanup()
