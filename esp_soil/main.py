# This is your main script.
import machine
import chirp
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


ssid = 'WmsonFamily'
password = 'Montana123'
mqtt_server = '10.0.0.179' # PI IP address
client_id = ubinascii.hexlify(machine.unique_id())
topic_pub = b'zone_1'
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

i2c = machine.I2C(0)
i2c = machine.I2C(1, scl=machine.Pin(22, machine.Pin.PULL_UP), sda=machine.Pin(21, machine.Pin.PULL_UP), freq=30000)
sensor = chirp.Chirp(bus=i2c, address=0x20)

print("Sensor Ready")
# while True:
#     print("moisture: ", sensor.moisture)
#     print("temp: ", sensor.temperature)
#     print("light: ", sensor.light)
#     print("moisture percentage: ", sensor.moist_percent)
#     time.sleep(5)


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

def measure_temp():
    while sensor.busy: print('sensor busy')
    print("polled temp: ",sensor.temperature) #documentation states inital read is junk value after long periods between read sessions
    while sensor.busy: print('sensor busy')
    t = sensor.temperature
    return t
  
def measure_moisture():
    while sensor.busy: print('sensor busy')
    print("polled moisture: ",sensor.moisture) #documentation states inital read is junk value after long periods between read sessions
    while sensor.busy: print('sensor busy')
    m = sensor.moisture
    return m

def measure_light():
    while sensor.busy: print('sensor busy')
    print("polled light: ",sensor.light()) #documentation states inital read is junk value after long periods between read sessions
    while sensor.busy: print('sensor busy')
    l = sensor.light()
    return l

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
      client.check_msg()
      temp = measure_temp()
      light = measure_light()
      moisture = measure_moisture()
      #if isinstance(temp, float) and isinstance(moisture, float) and isinstance(light, float):  # Confirm sensor results are numeric
      msg = (b'{0:3.1f},{1:3.1f},{0:3.1f}'.format(moisture, temp, light))
      client.publish(topic_pub, msg)  # Publish sensor data to MQTT topic
      print(msg)
      #else:
          #print('Invalid sensor readings.')
  except OSError:
      print('Failed to read sensor.')
      restart_and_reconnect()
  time.sleep(60)


