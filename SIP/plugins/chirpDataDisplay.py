# !/usr/bin/env python
# -*- coding: utf-8 -*-

import web  # web.py framework
import gv  # Get access to SIP's settings
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
        
        #print(db_client.get_list_database())
        db_client.switch_database('sensor_data')
        results = db_client.query('Select * from unshaded ORDER BY time DESC limit 25')
        #print(results.raw)
        points = list(results.get_points())
        i=0

        for p in points:
            print("Time: %s,Moisture: %i, Temp: %i" % (p['time'],p['moisture'],p['temperature']))
        #settings = points;  # Default settings. can be list, dictionary, etc.
        settings = points
        try:
            with open(
                u"./data/chirpDataDisplay.json",u"w"
                ) as f:
                    json.dump(settings,f)
        except Exception as e:
            print(u"file error: ",e)
            settings = {"FAILED"}
        return template_render.chirpDataDisplay(settings)  # open settings page


class updateTables(ProtectedPage):
    
    def POST(self):
        print("GOT INTO UPDATETABLE")
        qdict = web.data()
        print(qdict)
            
    
        db_client.switch_database('sensor_data')
        results = db_client.query('Select * from zone_1 ORDER BY time DESC limit 25')
        points = list(results.get_points())
        settings = points
        
        return settings

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
