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
mqtt_server = '192.168.1.135'
client_id = ubinascii.hexlify(machine.unique_id())
topic_pub = b'weather_station'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

sensor = dht.DHT22(machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP))   # DHT-22 on GPIO 15 (input with internal pull-up resistor)

print('Connection successful')
print(station.ifconfig())

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
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
      client.check_msg()
      sensor.measure()   # Poll sensor
      t = sensor.temperature()
      h = sensor.humidity()
      if isinstance(t, float) and isinstance(h, float):  # Confirm sensor results are numeric
          msg = (b'{0:3.1f},{1:3.1f}'.format(t, h))
          client.publish(topic_pub, msg)  # Publish sensor data to MQTT topic
          print(msg)
      else:
          print('Invalid sensor readings.')
  except OSError:
      print('Failed to read sensor.')
      restart_and_reconnect()
  time.sleep(4)