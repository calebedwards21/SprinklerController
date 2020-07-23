# SprinklerController

## MQTT
This is the protocol used 

## Flashing Micropython to ESP
- Start with the [DOCS](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)

> If using Windows, the esp will probably be on COM4

## DHT22
- PIN1 (VCC) - 5V
- PIN2 (DATA) - IO33
- PIN3 (NULL) - NO CONNECTION
- PIN4 (GND) - GND

## rshell
Open rshell

- `rhsell --buffer-size=30 -p COM4`

Copy file onto esp with rhsell

- `cp filename directory-on-esp`

Access repl when rshell is open

- `repl`