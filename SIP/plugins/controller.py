# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json  # for working with data file
import time
from threading import Thread
import web  # web.py framework
import gv  # Get access to SIP's settings
from urls import urls  # Get access to SIP's URLs
from sip import template_render  #  Needed for working with web.py templates
from webpages import ProtectedPage  # Needed for security
from helpers import load_programs
from influxdb import InfluxDBClient

db_client = InfluxDBClient(host='localhost',port=8086)

# Add new URLs to access classes in this plugin.
# fmt: off
urls.extend(
    [
        u"/contrl", u"plugins.controller.control_settings",
        u"/contrlupdate", u"plugins.controller.save_settings"
    ]
)
# fmt: on

# Add this plugin to the PLUGINS menu ["Menu Name", "URL"], (Optional)
gv.plugin_menu.append([_(u"Controller Plugin"), u"/contrl"])

# Empty settings dictionary to store all the data from the file.
settings = {}
# Empty programs list to store the programs of the SIP.
programs = []

# Read in the SIP programs
def load_prog():
    global programs
    try:
        with open(u"./data/programData.json", u"r") as f:  # Read the settings from file
            programs = json.load(f)
    except IOError:  #  If file does not exist create file with defaults.
        programs = []
    return programs

# Read in the settings from the file
def load_settings():
    global settings
    try:
        with open(u"./data/contrl.json", u"r") as f: # Open file to read settings
            settings = json.load(f)
    except IOError: # If the file does not exist, create a new file
        settings = {"watertime": "morning"}
        with open(u"./data/contrl.json", u"w") as f:
            json.dump(settings, f, indent=2, sort_keys=True)            
    return settings

# Call the load programs and settings methods.
load_prog()
load_settings()

# Call the load programs helper method to load the programs into SIP.
load_programs()


def timing_loop():
    print('start of timing loop')
    print(gv.now)
    last_min = 0
    while True:
        if int(gv.now // 60) != last_min:
            temp = int(gv.now // 60)
            t = time.localtime()
            time_stamp = time.strftime("%H:%M:%S",t)
            print(temp)
            print(time_stamp)
            last_min = int(gv.now // 60)
        time.sleep(60)
    


################
# Writing to DB#
################
def write_water_duration(zoneName,timeSec,timeMin):
    t = time.localtime() #can use gv.now as well?
    time_stamp = time.strftime("%H:%M:%S",t)
    date_stamp = time.strftime("%B %d,%Y",t)
    
    measurementName = zoneName + "_water_duration"
    
    data = [
            {
                "measurement": measurementName,
                "time": time_stamp,
                "date": date_stamp,
                "fields": {
                    "timeSec": timeSec,
                    "timeMin": timeMin
                }
            }
        ]
    db_client.write_points(data, database='sensor_data')
    print('End of writing water duration')

##############
# Web Pages: #
##############

class control_settings(ProtectedPage):
    """Load an html page for entering plugin settings."""

    def GET(self):
        try:
            with open(u"./data/contrl.json", u"r") as f1:  # Read settings from json file if it exists
                settings = json.load(f1)
            with open(u"./data/programData.json", u"r") as f2:
                programs = json.load(f2)
        except IOError:  # If file does not exist return empty value
            settings = {}  # Default settings.
            programs = []  # Default programs.
        
        station_count = [int(digit) for digit in bin(gv.sd['show'][0])[2:]]
        station_count.reverse()
        
        for n in range(len(station_count), 8):
            station_count.append(0)
        
        print(station_count)
        
        return template_render.controller(settings, programs, station_count)  # open settings page


class save_settings(ProtectedPage):
    """Save user input to contrl.json file."""

    def GET(self):
        settings = (web.input())  # Dictionary of values returned as query string from settings page.
        
        try:
            with open(u"./data/programData.json", u"r") as f:
                programs = json.load(f)
        except IOError:  # If file does not exist return empty value
            programs = []  # Default programs.
        
        # Load database stuff
        db_client.switch_database('sensor_data')
        bme_res = db_client.query('select * from weather_station ORDER BY time DESC limit 1')
        weather_station = list(bme_res.get_points())
        
        #add weather load of json
        try:
            with open(
                u"./data/weather.json",u"r"
                ) as f:
                    weather = json.load(f)
        except Exception as e:
            print(u"weather.json file error: ",e)
        
            weather = {"FAILED"}
        
        # Testing
        print(weather_station)
        print(settings)  
        print(len(programs))
        print("Programs load:", programs)
        
        # Check if the automated program exists
        temp = []
        for program in programs:
            name = program.get('name')            
            if not (name == 'seniorproject2020'):
                temp.append(program)
        programs = temp
        
        print("Programs remv:", programs)
            
        # Calculate time change
        custom_programs = []
        
        # Load station count
        station_count = [int(digit) for digit in bin(gv.sd['show'][0])[2:]]
        station_count.reverse()
        
        for n in range(len(station_count), 8):
            station_count.append(0)
        
        print(station_count)
        gpm = {
            "1" : 3.11,
            "2" : 3.3,
            "3" : 0.015,
            "4" : 0.25,
            "5" : 0.5,
            "6" : 1,
            "7" : 2,
            "8" : 0.2,
            "9" : 0.5,
            "10" : 0
        }
        
        for i in range(8):
            if station_count[i]:
                #Load zone data
                #Moisture
                #Watering Time
                m = db_client.query('Select * from zone_' + str(i+1) + ' ORDER BY time DESC limit 1')
                moisture = list(m.get_points())
                print(moisture)
                
                w_t = db_client.query('select * from zone_' + str(i+1) + '_water_duration ORDER BY time DESC limit 1')
                water_time = list(w_t.get_points())
                print(water_time)
                
                if ("hrate"+str(i+1)) in settings:
                    gpm["10"] = float(settings["hrate"+str(i+1)])
                
                precipitation_rate = 96.25 * gpm[settings["htype"+str(i+1)]] / float(settings["area"+str(i+1)])
                
                print("Precipitation Rate "+str(i+1)+":", precipitation_rate)
                
                time_minutes = round((float(settings["water"+str(i+1)]) / precipitation_rate) * 60)
                time_sec = time_minutes * 60
                
                print("Time Min"+str(i+1)+":", time_minutes)
                print("Time Sec"+str(i+1)+":", time_sec)
                
                station_mask = [1<<i]
                
                
                start_min = 360
                duration = [time_sec]
                stop_min = start_min+time_minutes
                
                zoneName = "zone_" + str(i+1)
                #write time to DB
                write_water_duration(zoneName,time_sec,time_minutes)
                
                #Add DB data to update duration water time
                
                day_mask = 127
                
                new_program = {
                    "cycle_min": 0,
                    "day_mask": day_mask,
                    "duration_sec": duration,
                    "enabled": 1,
                    "interval_base_day": 0,
                    "name": "seniorproject2020",
                    "start_min": start_min,
                    "station_mask": station_mask,
                    "stop_min": stop_min,
                    "type": "alldays"
                }
                
                custom_programs.append(new_program)
        
        # Add the new programs
        for prog in custom_programs:
            programs.append(prog)
        print(programs)
        
        # Save settings to file
        with open(u"./data/contrl.json", u"w") as f1:
            json.dump(settings, f1,  indent=2)  # save to file
        # Save changed SIP programs to file
        with open(u"./data/programData.json", u"w") as f2:
            json.dump(programs, f2,  indent=2)
        
        load_programs()
        # Begin Timing_Loop
        #tl = Thread(target=timing_loop)
        #tl.daemon = True
        #tl.start()
        
        
        raise web.seeother(u"/")  # Return user to home page.

class ProgramDataLoop(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
        self._sleep_time = 0
         
    def update(self):
        self._sleep_time = 0
        
    def _sleep(self,secs):
        self._sleep_time = secs
        while self._sleep_time > 0:
            time.sleep(1)
            self._sleep_time -= 1
            
    def run(self):
        print('start of timing loop')
        print(gv.now)
        last_min = 0
        while True:
            if int(gv.now // 60) != last_min:
                temp = int(gv.now // 60)
                t = time.localtime()
                en = settings['enabled']
                time_stamp = time.strftime("%H:%M:%S",t)
                print(temp)
                print(time_stamp)
                print(settings)
                last_min = int(gv.now // 60)
            self._sleep(60)
        

checker = ProgramDataLoop()
    

        
        