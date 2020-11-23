# !/usr/bin/env python
# -*- coding: utf-8 -*-

import web  # web.py framework
import gv  # Get access to SIP's settings
import datetime
from urls import urls  # Get access to SIP's URLs
from sip import template_render  #  Needed for working with web.py templates
from webpages import ProtectedPage  # Needed for security
import json  # for working with data file
from influxdb import InfluxDBClient


db_client = InfluxDBClient(host='localhost',port=8086)


# Add new URLs to access classes in this plugin.
# fmt: off
urls.extend([
    u"/chirpDataDisplay-sp", u"plugins.chirpDataDisplay.settings",
    u"/chirpDataDisplay-save", u"plugins.chirpDataDisplay.save_settings",
    u"/updateTables",u"plugins.chirpDataDisplay.updateTables"
    ])
# fmt: on

# Add this plugin to the PLUGINS menu ["Menu Name", "URL"], (Optional)
gv.plugin_menu.append([_(u"chirpDataDisplay Plugin"), u"/chirpDataDisplay-sp"])


def empty_function():  # Only a place holder
    
    pass


class settings(ProtectedPage):
    """
    Load an html page for entering plugin settings.
    """

    def GET(self):
        qdict = (
            web.input()
        )
        for key in qdict:
            print(qdict[key])
        
        db_client.switch_database('sensor_data')
        results = db_client.query('Select * from zone_1 ORDER BY time DESC limit 25')
        #print(results.raw)
        points = list(results.get_points())
        i=0
        
        bme_res = db_client.query('select * from weather_station ORDER BY time DESC limit 1')
        bme_vals = list(bme_res.get_points())
        for v in bme_vals:
            print("Time: %s, Temp: %i, Pressure: %i, Humidity: %i" % (v['time'],v['temperature'],v['pressure'],v['humidity']))

        #for p in points:
            #print("Time: %s,Moisture: %i, Temp: %i" % (p['time'],p['moisture'],p['temperature']))
            
        #Seperate Time and Date
        for i, p in enumerate(points):
            print(p['time'])
            print(str(p))
            d = p['time'][0:10]
            t = p['time'][11:19]
            print(t)
            print(d)
            p['time'] = t
            p['date'] = d
            print(str(p))
        #settings = points;  # Default settings. can be list, dictionary, etc.
        settings = points
        bme = bme_vals
        weather = {}
        
            
        try:
            with open(
                u"./data/weather.json",u"r"
                ) as f:
                    weather = json.load(f)
        except Exception as e:
            print(u"weather.json file error: ",e)
        
            weather = {"FAILED"}
        return template_render.chirpDataDisplay(settings,bme,weather)  # open settings page


class updateTables():
    
    def POST(self):
        print("GOT INTO UPDATETABLE")
        zoneSelected = web.data()
        print(zoneSelected)
            
    
        db_client.switch_database('sensor_data')
        results = db_client.query('Select * from ' + zoneSelected + ' ORDER BY time DESC limit 25')
        points = list(results.get_points())
        
        #Seperate Time and Date
        for i, p in enumerate(points):
            print(p['time'])
            print(str(p))
            d = p['time'][0:10]
            t = p['time'][11:19]
            print(t)
            print(d)
            p['time'] = t
            p['date'] = d
            print(str(p))
            #time_stamp = datetime.datetime.strptime(t,"%H:%M:%S")
            #print(time_stamp)
            
        settings = points
        ret = json.dumps(settings)
        
        return ret

class save_settings(ProtectedPage):
    """
    Save user input to json file.
    Will create or update file when SUBMIT button is clicked
    CheckBoxes only appear in qdict if they are checked.
    """

    def GET(self):
        qdict = (
            web.input()
        )  # Dictionary of values returned as query string from settings page.
        #        print qdict  # for testing
        
        for key in qdict:
            print(qdict[key])
        settings = {}   
   # save to file
        return template.render.chirpDataDisplay(settings)  # Return user to home page.


#  Run when plugin is loaded
empty_function()
