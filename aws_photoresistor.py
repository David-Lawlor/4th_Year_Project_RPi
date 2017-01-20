# reference
# http://www.raspberry-projects.com/pi/programming-in-python/i2c-programming-in-python/using-the-i2c-interface-2

import smbus
import RPi.GPIO as GPIO

DO = 17
GPIO.setmode(GPIO.BCM)

# smbus is a subset of i2c used for writing to an i2c device
# i2c is used for connecting low power peripherals to processors
bus = smbus.SMBus(1)


# PCF8591 address 'sudo i2cdetect -y 1'
address = 0x48

GPIO.setup(DO, GPIO.IN)

bus.write_byte(address, 0x40)
lux = bus.read_byte(address)  # dummy read needed
lux = bus.read_byte(address)

print 'lux = %d' % lux

