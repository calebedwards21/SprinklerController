import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import dht
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = 'EDWARDS2'
password = 'BENTCARD'
mqtt_server = '192.168.1.109'
client_id = ubinascii.hexlify(machine.unique_id())
topic_pub = b'weather_station'
# topic_sub = b'hello'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

sensor = dht.DHT22(machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP))   # DHT-22 on GPIO 15 (input with internal pull-up resistor)

print('Connection successful')
print(station.ifconfig())