import Adafruit_DHT
import RPi.GPIO as GPIO

# reference
# https://github.com/adafruit/Adafruit_Python_DHT/blob/master/examples/
# AdafruitDHT.py

# sensor type 11 Adafruit_DHT.DHT11
sensor_type = 11

# The GPIO pin that the sensor is connected to
GPIO_pin = 17

# Note that sometimes you won't get a reading and the results will be null
# (because Linux can't guarantee the timing of calls to read the sensor).
# If this happens try again!


def loop():
    while True:
    # Try to grab a sensor reading.  Use the read_retry method which will
    # retry up to 15 times to get a sensor reading (waiting 2 seconds between
    # each retry).
        humidity, temperature = Adafruit_DHT.read_retry(sensor_type, GPIO_pin)
        if humidity is not None and temperature is not None:
            print(('Temp={0:0.1f}*  Humidity={1:0.1f}%'
            .format(temperature, humidity)))

try:
    loop()
except KeyboardInterrupt:
    GPIO.cleanup()
