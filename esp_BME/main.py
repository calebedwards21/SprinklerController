# This is your main script.
import machine
from bme680 import *
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()



#Personal WIFI
ssid = 'WmsonFamily'
password = 'Montana123'
mqtt_server = '10.0.0.179' # PI IP address

#LAN Router
#ssid = 'SprinklerProject'
#password = 'RainRainGoAway'
#mqtt_server = '192.168.1.3' # PI IP address

client_id = ubinascii.hexlify(machine.unique_id())
topic_pub = b'weather_station'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid,password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

#Setup Sensor BME280
#i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21), freq=30000)
#bme = bme280.BME280(i2c=i2c)

#Setup Sensor BME680
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21), freq=30000)
bme = BME680_I2C(i2c=i2c)

print("Sensor Ready")


def connect_and_subscribe():
    global client_id, mqtt_server
    client = MQTTClient(client_id, mqtt_server)
    # client.set_callback(sub_cb)
    client.connect()
    print('Connected to %s MQTT broker' % (mqtt_server))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()



try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
      #client.check_msg()
      print('just before sensor reads')

      #BME280 Polling
      #t,p,h = bme.values
      #t1 = float(t)
      #p1 = float(p)
      #h1 = float(h)

      #BME680 Polling
      temp = round(bme.temperature,1)
      pres = round(bme.pressure,1)
      humid = round(bme.humidity,1)
      gas = bme.gas/1000

      print(gas)
      msg = (b'{0:3.1f},{1:3.1f},{2:3.1f}'.format(temp, pres, humid))
      client.publish(topic_pub, msg)  # Publish sensor data to MQTT topic
      print(msg)
      
  except OSError:
      print('Failed to read sensor.')
      restart_and_reconnect()
  time.sleep(60)


