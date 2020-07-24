import paho.mqtt.client as mqtt
import time
import threading
from influxdb import InfluxDBClient

TOPICS = ['temp_humidity', 'hello']
db_client = InfluxDBClient(host='localhost', port=8086)
db_client.create_database('sensor_data')	


def write_data(temp, humidity):
	data_end_time = int(time.time() * 1000) #ms - need to change to more readable time
	data = [
	{
		"measurement": "temperature",
		"time": data_end_time,
		"fields": {
			"temperature": temp
		}		
	},
	{
		"measurement": "humidity",
		"time": data_end_time,
		"fields": {
			"humidity": humidity
		}
	}	
	]
	db_client.write_points(data, database='sensor_data')	

def on_connect(client, userdata, flags, rc):
	if rc==0:
		print('Connection OK  with result code {0}'.format(rc))
	else:
		print('Connection Bad with result code {0}'.format(rc))
	for topic in TOPICS:
		client.subscribe(topic)

def on_message(client, userdata, msg):
	if msg.topic == 'temp_humidity':
		t,h = [float(x) for x in msg.payload.decode('utf-8').split(',')]
		t = t * 9/5 + 32
		print('{0}F {1}%'.format(t,h))
		write_data(t,h)
	elif msg.topic == 'count':
		print(msg)
	elif msg.topic == 'hello':
		print(msg.payload)
	else:
		print(msg.topic)


def esp_data():
	client = mqtt.Client()
	client.on_connect = on_connect
	time.sleep(2)
	client.on_message = on_message
	client.connect('localhost', 1883, 60)
	client.loop_forever()


t = threading.Thread(target=esp_data)
t.start()

