# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json  # for working with data file
import time  # for delaying the program

import web  # web.py framework
import gv  # Get access to SIP's settings
from blinker import signal # Used to check for zone singals
from urls import urls  # Get access to SIP's URLs
from sip import template_render  #  Needed for working with web.py templates
from webpages import ProtectedPage  # Needed for security
from helpers import restart

from gpiozero.pins.native import NativeFactory
from gpiozero import DigitalOutputDevice

# Tell SIP to not use gpio
gv.use_gpio_pins = False
# Set the delay between zone changes to 5 seconds
gv.sd["sdt"] = 5

# Add new URLs to access classes in this plugin.
# fmt: off
urls.extend(
    [
        u"/relay", u"plugins.relay_plugin.relay_settings",
        u"/relayupdate", u"plugins.relay_plugin.save_settings"
    ]
)
# fmt: on

# Add this plugin to the PLUGINS menu ["Menu Name", "URL"], (Optional)
gv.plugin_menu.append([_(u"Relay Plugin"), u"/relay"])

# Empty settings dictionary to store all the data from the file.
settings = {}

# Read in the settings from the file
def load_settings():
    global settings
    try:
        with open(u"./data/relay.json", u"r") as f: # Open file to read settings
            settings = json.load(f)
    except IOError: # If the file does not exist, create a new file
        settings = {u"relay1":27,u"relay2":22,u"relay3":23,u"relay4":24}
        with open(u"./data/relay.json", u"w") as f:
            json.dump(settings, f, indent=2, sort_keys=True)
     
    print(settings)
     
    return settings

# Call the load settngs method to load all the settings from the file.
load_settings()

# GPIO Zero factory setting
factory = NativeFactory()

try:
    output_pins = {}
    
    if gv.platform == u"pi":
        #pins_dict = settings.copy()
        #pins = list(pins_dict.values())
        for zone, pin in settings.items():
            output_pins.update({int(zone[-1])-1 : DigitalOutputDevice(pin, False, pin_factory=factory)})
        
    else:
        print(u"Relay Plugin only supports raspberry pi.")
except:
    print(u"Relay Plugin: GPIO pins not able to be set.")



def sprinkler_zone_call(arg):
    """Switch the relays when the core program blinker tells to change zone state"""
    print(gv.sd['mton'])
    print(gv.sd['mtoff'])
    print(gv.sd['sdt'])
    with gv.output_srvals_lock:
        for station, output_pin in output_pins.items():
            try:
                # If the station is on
                if gv.output_srvals[station]:
                    output_pin.on()
                # If the station is off
                else:
                    output_pin.off()
            except Exception as e:
                print(u"Relays were unable to switch", e, i+1)

sprinkler_zones = signal(u"zone_change")
sprinkler_zones.connect(sprinkler_zone_call)

##############
# Web Pages: #
##############

class relay_settings(ProtectedPage):
    """Load an html page for entering relay board plugin settings."""

    def GET(self):
        try:
            with open(u"./data/relay.json", u"r") as f:  # Read settings from json file if it exists
                settings = json.load(f)
        except IOError:  # If file does not exist return empty value
            settings = {}  # Default settings. can be list, dictionary, etc.
            
        station_count = [int(digit) for digit in bin(gv.sd['show'][0])[2:]]
        station_count.reverse()
        
        for n in range(len(station_count), 8):
            station_count.append(0)
            
        return template_render.relay_plugin(settings, station_count)  # open settings page


class save_settings(ProtectedPage):
    """Save user input to relay.json file."""

    def GET(self):
        qdict = web.input() # Dictionary of values returned as query string from settings page.
        
        # Convert string values to ints
        for key in qdict:
            qdict[key] = int(qdict[key])
            
        print(qdict)  # for testing
            
        with open(u"./data/relay.json", u"w") as f:
            json.dump(qdict, f, indent=2, sort_keys=True)  # save to file
        raise web.seeother(u"/restart")  # Return user to home page.
    

