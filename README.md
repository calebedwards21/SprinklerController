# SprinklerController

## Git
We needed to create a git repo that contained the repo from a third party.
This would be a submodule, which we will use for pulling in SIP
`git submodule add clone_link repo_name`

> Resource : [git-submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

## Creating a Virtual Environment for Python
- We need Python3 to run any of our ML files
- `Python3 -m venv env-name`
> Activate with the command `source env-name/bin/activate`

We will all want the same version of Python with the same packages
After creating the virtual environment install the pip packages from requirements.txt
`python3 -m pip install -r requirements.txt`
>This way you will not need to install any of the pip packages required below

## Flashing Micropython to ESP
Start with the [DOCS](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)

> If using Windows, the port will be on COM#

- The initial file that will be run on the esp using micropython will be boot.py followed with main.py

## rshell
rshell is used for flashing files to the esp and opening a repl to the esp.

Open rshell

- `rhsell -p COM4`

Copy file onto esp with rhsell

- `cp filename directory-on-esp`

Access repl when rshell is open

- `repl`

> The repl is useful for visualizing output from the esp. If you have print statements in the esp code it will be shown in the repl.

## ampy
Ampy is used to flash files to esp, like boot.py and main.py

- ampy --port COM ls/put/get filename

## Running our PI_SERVER on startup
- use the rc.local file in `/etc/rc.local`
- Example : 
> cd directory/containing/script
> python script.py

## Installations
### Sklearn
- pip install -U scikit-learn
> If any installation errors occur, possible fix `sudo apt-get install libatlas-base-dev`

### Influx
-Install locally
[InfluxDB Download Page](https://portal.influxdata.com/downloads/)

- Install on Python
`pip install influxdb`

## MQTT
This is the protocol used for wireless connection. This uses the Wifi for publish/subscribes.
> [Mosquitto Broker for Linux](https://mosquitto.org/)
### Mosquitto
- Install the broker
`sudo apt install -y mosquitto mosquitto-clients`
- Auto start on boot
`sudo systemctl enable mosquitto.service`

-Install on Python
`pip install paho-mqtt`

## DHT22
- PIN1 (VCC) - 5V
- PIN2 (DATA) - IO33 - Or any IO Pin
- PIN3 (NULL) - NO CONNECTION
- PIN4 (GND) - GND

## Moisture Sensor
- VCC - 5/3.3 V - This value changes the readings
- GND - GND
- SDA - IO21 / IO4 - Or any IO Pin
- SCL - IO22 / IO5 - Or any IO Pin
- Library: https://github.com/scopelemanuele/pyChirpLib

## BME680
- VCC - 5/3.3v
- GND - GND
- SDA - GPIO 21
- SCL- GPIO 22
- Library: https://randomnerdtutorials.com/micropython-bme680-esp32-esp8266/

## I2C Micropython ESP32

The hardware version of I2C has to be used with Micropython. The software side doesn't work.

Set up your I2C connection with the machine library

``` python
i2c = machine.I2C(0)
i2c = machine.I2C(1, sda, scl, freq)
```

## Equation
[Penman-Monteith](http://www.fao.org/3/X0490E/x0490e06.htm) - This equation will tell you how much water has evaporated from your yard during the day and can be used for algorithm creation.

Sensors Needed:

- Temperature
- Radiation - These sensors are expensive / Need to find some weather API that has a radiation sensor, or create our own
- Wind Speed
- Humidity

[Machine Learning](https://www.analyticsvidhya.com/blog/2017/09/common-machine-learning-algorithms/) - Supervised learning

We will need weather data, like from the sensors we have, that has correct output of how much water we need. This is how the model will learn, and we can use our sensor's data to learn from this model

- Linear Regression 
- Need to find some historical data that has this info 

## Interface
### SIP
NOTE: Must clone repo in PI users home directory (pi@raspberrypi:~$) EXAMPLE: /home/pi/SprinklerController

Setting up SIP to automatically execute on reboot 

 1.) Copy Script file sip.service to /etc/systemd/system. Run command:
     sudo cp SprinklerController/SIP/sip.service /etc/systemd/system/
     
 2.) Enable sip.service. Run command:
     sudo systemctl enable sip.service
     
 3.) Reboot PI. Run command:
     sudo reboot

Check status,start,stop and restart SIP Interface with terminal commands:

- Disable auto-start: sudo systemctl disable sip.service
 
- Status: systemctl status sip
 
- Start: sudo systemctl start sip
 
- Stop: sudo systemctl stop sip
 
- Restart: sudo systemctl restart sip

See offical SIP Irrigational Control open source git hub project: https://dan-in-ca.github.io/SIP/
