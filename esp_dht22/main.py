def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'hello':
    print('ESP received hello message')

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
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