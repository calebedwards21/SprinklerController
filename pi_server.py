import paho.mqtt.client as mqtt
import time
import threading
from influxdb import InfluxDBClient
from sprinkler_ml import ML_Sprinkler 
from weather_scraper import Scraper

db_client = InfluxDBClient(host='localhost', port=8086) #Database
db_client.create_database('sensor_data')

model = ML_Sprinkler() #Machine Learning Model
model.create_model()

scraper = Scraper() #Weather Scraper
scraper.create_scraper()

TOPICS = ['zone_1', 'zone_2', 'zone_3', 'weather_station'] #Topics to subscribe to


def write_hub(temp, humidity):
    """
    Rcv data from the hub and store in the database
    """
    
    #Create DB input from data received from hub topic
    time = time.localtime()
    time_stamp = time.strftime("%A, %B %d,%Y %H:%M:%S", time)
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
    
    #Write data to database
    db_client.write_points(data, database='sensor_data')
    print(f'End of writing hub')


def write_zone(zone, moisture, temp, light): #Need to edit this if were not using light
    """
    Rcv data from a zone esp and store in database
    """
    
    #Create DB input from data from one of the zone topics
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
    
    #Write the data to the database
    db_client.write_points(data, database='sensor_data')
    print(f'End of writing zone : {zone}')
    
    # Output scraped data to json files
    if zone == "zone_1":
        scraper.write_file()


def on_message(client, userdata, msg):
    """
    Initial rcv/subscribe when a message gets published
    """
    if msg.topic == 'weather_station':
        print("Received weather_station topic")
        t,h = [float(x) for x in msg.payload.decode('utf-8').split(',')]
        t = t * 9/5 + 32
        print(('{0}F {1}%'.format(t,h)))
        write_hub(t,h)
    elif msg.topic == 'zone_1' or msg.topic == 'zone_2' or msg.topic == 'zone_3':
        print(f'Received Zone topic : {msg.topic}')
        m,t,l = [float(x) for x in msg.payload.decode('utf-8').split(',')]
        temp = t * 9/5 + 32
        print(f'Temp : {temp}, Moisture : {m}, Light : {l}')
        write_zone(msg.topic,m,temp,l)
    else:
        print((msg.topic))
        
        
def on_connect(client, userdata, flags, rc):
    """
    Connect to the broker and subscribe to all topics    
    """
    if rc==0:
        print(('Connection OK  with result code {0}'.format(rc)))
    else:
        print(('Connection Bad with result code {0}'.format(rc)))
    for topic in TOPICS:
        client.subscribe(topic)


def esp_data():
    """
    Initial setup of the pi server and the broker
    """
    client = mqtt.Client()
    client.on_connect = on_connect
    time.sleep(2)
    client.on_message = on_message
    client.connect('localhost', 1883, 60)
    client.loop_forever()


if __name__ == "__main__":
    """
    Starting point for server
    """
    esp_data()
