# SprinklerController
<<<<<<< HEAD

## MQTT
This is the protocol used for wireless connection. This uses the Wifi for publish/subscribes.

## Flashing Micropython to ESP
Start with the [DOCS](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)

> If using Windows, the port will be on COM#

- The initial file that will be run on the esp using micropython will be boot.py followed with main.py

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

## I2C Micropython ESP32

The hardware version of I2C has to be used with Micropython. The software side doesn't work.

Set up your I2C connection with the machine library

``` python
i2c = machine.I2C(0)
i2c = machine.I2C(1, sda, scl, freq)
```

## Equation
[Penman-Monteith](http://www.fao.org/3/X0490E/x0490e06.htm) - This equation will tell you how much water has evaporated from your yard during the day.

Sensors Needed:

- Temperature
- Radiation - These sensors are expensive / Need to find some weather API that has a radiation sensor, or create our own
- Wind Speed
- Humidity

[Machine Learning](https://www.analyticsvidhya.com/blog/2017/09/common-machine-learning-algorithms/) - Supervised learning

We will need weather data, like from the sensors we have, that has correct output of how much water we need. This is how the model will learn, and we can use our sensor's data to learn from this model

- Linear Regression 
- Need to find some historical data that has this info 
=======
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
>>>>>>> Interface
