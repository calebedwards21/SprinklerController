# This is your main script.
import machine
import chirp
from time import sleep

i2c = machine.I2C(0)
i2c = machine.I2C(1, scl=machine.Pin(22, machine.Pin.PULL_UP), sda=machine.Pin(21, machine.Pin.PULL_UP), freq=30000)
sensor = chirp.Chirp(bus=i2c, address=0x20)
print("Sensor Ready")
while True:
    print("moisture: ", sensor.moisture)
    print("temp: ", sensor.temperature)
    sleep(5)