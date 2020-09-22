# SprinklerController

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