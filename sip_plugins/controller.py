# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from threading import Thread
from random import randint
import json  # for working with data file
import time
import sys
import traceback

import web  # web.py framework
import gv  # Get access to SIP's settings
from blinker import signal # Used to check for zone singals
from urls import urls  # Get access to SIP's URLs
from sip import template_render  #  Needed for working with web.py templates
from webpages import ProtectedPage  # Needed for security
from helpers import load_programs

from helpers import get_rpi_revision

from gpiozero.pins.native import NativeFactory
from gpiozero import Button

# FLow Sensor
# Tell SIP to not use gpio
gv.use_gpio_pins = False

# GPIO Zero factory setting
factory = NativeFactory()

# GPIO Zero sensor setup
inpt = 17  # use for gpiozero GPIO 27, pin 13
#sensor = Button(input, pull_up=False, bounce_time=10, pin_factory=factory)
sensor = Button(inpt, pull_up=False, pin_factory=factory)

# Variables for tracking pulse count
global rate_cnt
rate_cnt = 0  # Rate of counts (L/min)

# Pressure Sensor
# I2C bus Rev Raspi RPI=1 rev1 RPI=0 rev0
try:
    import smbus  # for YL-40 PFC 8591 A/D

    ADC = smbus.SMBus(1 if get_rpi_revision() >= 2 else 0)
except ImportError:
    ADC = None

# Add new URLs to access classes in this plugin.
# fmt: off
urls.extend(
    [
        u"/controller", u"plugins.controller.controller_settings",
        u"/controllerupdate", u"plugins.controller.save_settings"
    ]
)
# fmt: on

# Add this plugin to the PLUGINS menu ["Menu Name", "URL"], (Optional)
gv.plugin_menu.append([_(u"Controller Plugin"), u"/controller"])

################################################################################
# Program data function loop:                                                   #
################################################################################

# Put data loop class here

################################################################################
# Flow Sensor function loop:                                                   #
################################################################################

class FlowSender(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
        self.status = ""

        self._sleep_time = 0
        
    def add_status(self, msg):
        if self.status:
            self.status += "\n" + msg
        else:
            self.status = msg
        print(msg)
        
    def update(self):
        self._sleep_time = 0

    def _sleep(self, secs):
        self._sleep_time = secs
        while self._sleep_time > 0:
            time.sleep(1)
            self._sleep_time -= 1
            
    def run(self):
        global rate_cnt
        time.sleep(
            randint(3, 10)
        )  # Sleep some time to prevent printing before startup information
        print("Water Flow sensor plugin is active")
        last_time = gv.now

        while True:
            try:
                flow_settings = get_flow_options()  # load data from file
                #if flow_settings["use_flow"] != "off":  # if flow plugin is enabled
                if (flow_settings["use_log"] == "on" and flow_settings["time"] != "0"
                ):  # if log is enabled and time is not 0 min
                    actual_time = gv.now
                    if actual_time - last_time > (
                        int(flow_settings["time"]) * 60
                    ):  # if is time for save pulses is only needed
                        pulse_count = get_now_count()
                        gpm_val = calc_gpm(pulse_count)
                        last_time = actual_time
                        self.status = ""
                        TEXT = (
                            "On "
                            + time.strftime(
                                "%d.%m.%Y at %H:%M:%S", time.localtime(time.time())
                            )
                            + " save Water Flow sensor data pulse count = " + str(pulse_count)
                            + " and gpm conversion = " + str(gpm_val)
                        )
                        self.add_status(TEXT)
                        write_flow_log(gpm_val)
                        
                self._sleep(1)
                

            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err_string = "".join(
                    traceback.format_exception(exc_type, exc_value, exc_traceback)
                )
                self.add_status("Flow Sensor plugin encountered error: " + err_string)
                self._sleep(5)

checker_flow = FlowSender()

################################################################################
# Pressure Sensor function loop:                                               #
################################################################################

class PressureSender(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
        self.status = ""

        self._sleep_time = 0

    def add_status(self, msg):
        if self.status:
            self.status += "\n" + msg
        else:
            self.status = msg
        print(msg)

    def update(self):
        self._sleep_time = 0

    def _sleep(self, secs):
        self._sleep_time = secs
        while self._sleep_time > 0:
            time.sleep(1)
            self._sleep_time -= 1

    def run(self):
        time.sleep(
            randint(3, 10)
        )  # Sleep some time to prevent printing before startup information
        print("Pressure sensor plugin is active")
        last_time = gv.now

        while True:
            try:
                pressure_settings = get_pressure_options()  # load data from file
                #if pressure_settings["use_pressure"] != "off":  # if pressure plugin is enabled
                if (pressure_settings["use_log"] == "on" and pressure_settings["time"] != "0"
                ):  # if log is enabled and time is not 0 min
                    actual_time = gv.now
                    if actual_time - last_time > (
                        int(pressure_settings["time"]) * 60
                    ):  # if is time for save ad2 is only needed
                        ad2 = get_now_measure()
                        ad2 = get_volt(ad2)
                        ad2 = get_psi(ad2)
                        last_time = actual_time
                        self.status = ""
                        TEXT = (
                            "On "
                            + time.strftime(
                                "%d.%m.%Y at %H:%M:%S", time.localtime(time.time())
                            )
                            + " save Pressure sensor data PSI= " + str(ad2)
                        )
                        self.add_status(TEXT)
                        write_pressure_log(ad2)

                self._sleep(1)

            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err_string = "".join(
                    traceback.format_exception(exc_type, exc_value, exc_traceback)
                )
                self.add_status("Pressure Sensor plugin encountered error: " + err_string)
                self._sleep(5)


checker_pressure = PressureSender()

################################################################################
# Program Data Helper functions:                                               #
################################################################################

#

################################################################################
# Flow Helper functions:                                                       #
################################################################################

def pressed():
    """Count meter pulses from hall effect
       called from gpiozero 'interrupt'
       callback.
    """
    global rate_cnt 
    rate_cnt += 1
    #print(rate_cnt)  # CAN REMOVE THIS - USED TO DEBUG

def calc_gpm(pulse_count):
    """Return gpm flow from count"""
    # PATRICK --- WE NEED TO FIGURE THIS OUT FOR THE ACTUAL FLOW RATE (LPM and GPM)
    # FROM THE NUMBER OF PULSES AND THE TOTAL TIME IN SECONDS THAT HAVE ELAPSED
    
    # From the sensor specification data sheet:
    # Calculate Liters per minute using sensor specification
    # F = Constant * units of flow (liter per min) * time (seconds)
    # ~ 330 pulse/liter
    
    # To calculate Liters per minute
    constant = 10 ### PATRICK NEED TO FIGURE THE CONSTANT VALUE OUT
    time_seconds = 60  ### since this function is called every minute
    lpm = round((constant * (pulse_count / 330.0) / (time_seconds / 60)), 2)
    
    # Convert lpm to gpm
    gpm = round(lpm * 0.26417205236)
    return gpm

def get_now_count():
    """Return number of pulse counts from the GPIO to webpage"""
    global rate_cnt
    try:
        sensor.when_released = pressed
        return rate_cnt
    except AttributeError:
        return "0"

def get_flow_options():
    """Returns the data from file."""
    flow_settings = {
        "use_log": "off",
        "time": "0",
        "records": "0",
        "pulsesval": get_now_count(),
        "status": checker_flow.status,
    }
    try:
        with open("./data/flow_sensor.json", "r") as f:  # Read the settings from file
            file_data = json.load(f)
        for key, value in file_data.iteritems():
            #print(key, value)
            if key in flow_settings:
                flow_settings[key] = value
    except IOError:
        defaultflow = {
        "use_log": "off",
        "time": "0",
        "records": "0",
        "pulsesval": 0,
        "status": "",
        }

        with open("./data/flow_sensor.json", "w") as f:  # write defalult settings to file
            json.dump(defaultflow, f)

    except Exception:
        pass

    return flow_settings

def read_flow_log():
    """Read flow log"""
    try:
        with open("./data/flowlog.json") as logf:
            records = logf.readlines()
        return records
    except IOError:
        return []
    
def write_flow_log(pulses):
    """Add run data to csv file - most recent first."""
    flow_settings = get_flow_options()
    logline = (
        '{"Time":"'
        + time.strftime('%H:%M:%S","Date":"%d-%m-%Y"', time.gmtime(gv.now))
        + ',"Flow":"'
        + str(pulses)
        + '"}\n'
    )
    print(logline)
    log = read_flow_log()
    log.insert(0, logline)
    with open("./data/flowlog.json", "w") as f:
        if int(flow_settings["records"]) != 0:
            f.writelines(log[: int(flow_settings["records"])])
        else:
            f.writelines(log)
    return

################################################################################
# Pressure Helper functions:                                                   #
################################################################################

def get_psi(data):
    """Return PSI value from voltage"""
    max_sensor_psi = 100   # Also 30 
    psi = (data - 0.51) * (max_sensor_psi / 4)
    psi = round(psi, 0)
    return psi

def get_volt(data):
    """Return voltage 0-5V from number"""
    volt = (data * 5.0) / 255
    #volt = round(volt, 1)
    return volt

def get_now_measure():
    """Return number 0-255 from A/D PFC8591 module to webpage"""
    try:
        AD_pin = 2 # Using ADIn2 channel
        ADC.write_byte_data(0x48, (0x40 + AD_pin), AD_pin)
        ad_val = ADC.read_byte(0x48)
        return ad_val
    except AttributeError:
        return "0"

def get_pressure_options():
    """Returns the data from file."""
    pressure_settings = {
        "use_log": "off",
        "time": "0",
        "records": "0",
        "ad2val": get_now_measure(),
        "status": checker_pressure.status,
    }
    try:
        with open("./data/pressure_sensor.json", "r") as f:  # Read the settings from file
            file_data = json.load(f)
        for key, value in file_data.iteritems():
            if key in pressure_settings:
                pressure_settings[key] = value
    except IOError:
        defaultpressure = {
        "use_log": "off",
        "time": "0",
        "records": "0",
        "ad2val": 0,
        "status": "",
        }

        with open("./data/pressure_sensor.json", "w") as f:  # write defalult settings to file
            json.dump(defaultpressure, f)

    except Exception:
        pass

    return pressure_settings


def read_pressure_log():
    """Read pressure log"""
    try:
        with open("./data/pressurelog.json") as logf:
            records = logf.readlines()
        return records
    except IOError:
        return []


def write_pressure_log(ad2):
    """Add run data to csv file - most recent first."""
    pressure_settings = get_pressure_options()
    logline = (
        '{"Time":"'
        + time.strftime('%H:%M:%S","Date":"%d-%m-%Y"', time.gmtime(gv.now))
        + ',"Pressure":"'
        + str(ad2)
        + '"}\n'
    )
    print(logline)
    log = read_pressure_log()
    log.insert(0, logline)
    with open("./data/pressurelog.json", "w") as f:
        if int(pressure_settings["records"]) != 0:
            f.writelines(log[: int(pressure_settings["records"])])
        else:
            f.writelines(log)
    return

################################################################################
# File Loading functions:                                                      #
################################################################################

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
        with open(u"./data/controller.json", u"r") as f: # Open file to read settings
            settings = json.load(f)
    except IOError: # If the file does not exist, create a new file
        settings = {"watertime": "morning"}
        with open(u"./data/controller.json", u"w") as f:
            json.dump(settings, f, indent=2, sort_keys=True)            
    return settings

# Call the load programs and settings methods.
load_prog()
load_settings()

# Call the load programs helper method to load the programs into SIP.
load_programs()

################################################################################
# Blinker Functions:                                                           #
################################################################################

global prev_state, curr_state, old_time
curr_state = gv.output_srvals.copy()

def station_measure_count(name, **kw):
    """Measure the station's flow rate and pressure while active"""
    global prev_state, curr_state, rate_cnt, old_time
    
    with gv.output_srvals_lock:
        
        prev_state = curr_state.copy()
        curr_state = gv.output_srvals.copy()
        
        for station in range(8):
            if curr_state[station] and not prev_state[station]:
                print("FLOW Station", station+1, "Start")
                # Set the old time
                old_time = gv.now
                # Reset the flow count
                rate_cnt = 0
                # Wait a few seconds, then grab the pressure
                time.sleep(4)
                press = get_now_measure()
                press = get_volt(press)
                press = get_psi(press)
                print("Pressure PSI", press)
                
            elif prev_state[station] and not curr_state[station]:
                # Count the time difference
                seconds = gv.now-old_time
                print("FLOW Station", station+1, "End", seconds)
                # Grab the flow rate count and caclulate measures
                pulses = rate_cnt
                pps = rate_cnt/seconds
                mlps = pps*3.0303
                mlpm = mlps*60
                lpm = mlpm/1000
                gpm = lpm*0.2641720524
                print("GPM", gpm)

sprinkler_zone_change = signal(u"zone_change")
sprinkler_zone_change.connect(station_measure_count)

################################################################################
# Web Pages:                                                                   #
################################################################################

class controller_settings(ProtectedPage):
    """Load an html page for entering plugin settings."""

    def GET(self):
        try:
            with open(u"./data/controller.json", u"r") as f1:  # Read settings from json file if it exists
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
    """Save user input to controller.json file."""

    def GET(self):
        settings = (web.input())  # Dictionary of values returned as query string from settings page.
        
        try:
            with open(u"./data/programData.json", u"r") as f:
                programs = json.load(f)
        except IOError:  # If file does not exist return empty value
            programs = []  # Default programs.
        
        # Load database stuff
        
        # Testing
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
        with open(u"./data/controller.json", u"w") as f1:
            json.dump(settings, f1,  indent=2)  # save to file
        # Save changed SIP programs to file
        with open(u"./data/programData.json", u"w") as f2:
            json.dump(programs, f2,  indent=2)
        
        load_programs()
        
        raise web.seeother(u"/")  # Return user to home page.
    