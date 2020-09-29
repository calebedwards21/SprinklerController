import paho.mqtt.client as mqtt
import time
import threading
from influxdb import InfluxDBClient

TOPICS = ['zone_1', 'zone_2', 'zone_3', 'weather_station']
db_client = InfluxDBClient(host='localhost', port=8086)
db_client.create_database('sensor_data')


def write_hub(temp, humidity):        
	t = time.localtime()
        time_stamp = time.strftime("%A, %B %d,%Y %H:%M:%S",t)
        print(time_stamp)
	data = [
	{
		"measurement": "hub_temperature",
		"time": time_stamp,
		"fields": {
			"temperature": temp
		}
	},
	{
		"measurement": "hub_humidity",
		"time": time_stamp,
		"fields": {
			"humidity": humidity
		}
	}
	]
	db_client.write_points(data, database='sensor_data')


def write_zone(zone, moisture, temp, light):
        t = time.localtime()
        time_stamp = time.strftime("%A, %B %d,%Y %H:%M:%S",t)
        print(time_stamp)
	data = [
	{
		"measurement": zone,
		"time": time_stamp,
		"fields": {
			"moisture": moisture,
			"temperature": temp,
			"light": light
		}
	}
	]
	db_client.write_points(data, database='sensor_data')
	print("End of writing zone")


def on_connect(client, userdata, flags, rc):
	if rc==0:
		print('Connection OK  with result code {0}'.format(rc))
	else:
		print('Connection Bad with result code {0}'.format(rc))
	for topic in TOPICS:
		client.subscribe(topic)


def on_message(client, userdata, msg):
	if msg.topic == 'weather_station':
		print("Received weather_station topic")
		t,h = [float(x) for x in msg.payload.decode('utf-8').split(',')]
		t = t * 9/5 + 32
		print('{0}F {1}%'.format(t,h))
		write_hub(t,h)
	elif msg.topic == 'zone_1' or msg.topic == 'zone_2' or msg.topic == 'zone_3':
		print("Received Zone topic")
		print(msg.topic)
    		m,t,l = [float(x) for x in msg.payload.decode('utf-8').split(',')]
		temp = t * 9/5 + 32
		print('Temperature: ',temp)
		print('Moisture: ',m)
		print('Light: ',l)
		write_zone(msg.topic,m,temp,l)
	else:
		print(msg.topic)


def esp_data():
	client = mqtt.Client()
	client.on_connect = on_connect
	time.sleep(2)
	client.on_message = on_message

	connected = 0
#	while connected == 0:
#		try:
#			client.connect('localhost', 1883, 60)
#			connected = 1	
#		except:
#			print("retrying connection")
#			time.sleep(1)
	client.connect('localhost', 1883, 60)
	client.loop_forever()


# t = threading.Thread(target=esp_data)
# t.start()
esp_data()
