import paho.mqtt.client as mqtt
import time
import threading
from influxdb import InfluxDBClient
from weather_scraper import Scraper

TOPICS = ['zone_1', 'zone_2', 'zone_3', 'weather_station']

db_client = InfluxDBClient(host='localhost', port=8086)
db_client.create_database('sensor_data')

#scraper = Scraper() #Weather Scraper
#scraper.create_scraper()

def write_hub(temp,pressure,humidity):
        """
        Writes hub data to DB
        """
        t = time.localtime()
        time_stamp = time.strftime("%H:%M:%S",t)
        date_stamp = time.strftime("%B %d,%Y",t)
        print(time_stamp)
        print(date_stamp)
        data = [
        {
            "measurement": "weather_station",
            "time": time_stamp,
                    "date": date_stamp,
            "fields": {
                "temperature": temp,
                            "pressure": pressure,
                            "humidity": humidity
            }
        }
        ]
        db_client.write_points(data, database='sensor_data')


def write_zone(zone, moisture, temp, light):
        """
        Writes zone data to DB
        """
        t = time.localtime()
        time_stamp = time.strftime("%H:%M:%S",t)
        date_stamp = time.strftime("%B %d,%Y",t)
        print(time_stamp)
        print(date_stamp)
        data = [
        {
            "measurement": zone,
            "time": time_stamp,
                    "date": date_stamp,
            "fields": {
                "moisture": moisture,
                "temperature": temp
            }
        }
        ]
        db_client.write_points(data, database='sensor_data')
        print("End of writing zone")

        # Output scraped data to json files
        #if zone == "zone_2" or zone == "zone_1":
            #scraper.write_file()
            #print("wrote file")


def on_message(client, userdata, msg):
        """
        Initial rcv/subscribe when a message gets published
        """
        if msg.topic == 'weather_station':
            print("Received weather_station topic")
            t,p,h = [float(x) for x in msg.payload.decode('utf-8').split(',')]
            t = t * 9/5 + 32
            print(('{0}F {1}hPa {2}%'.format(t,p,h)))
            write_hub(t,p,h)
        elif msg.topic == 'zone_1' or msg.topic == 'zone_2' or msg.topic == 'zone_3':
            print("Received Zone topic")
            print((msg.topic))
            m,t,l = [float(x) for x in msg.payload.decode('utf-8').split(',')]
            temp = t * 9/5 + 32
            print(('Temperature: ',temp))
            print(('Moisture: ',m))
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

