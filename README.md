[![Build Status](https://travis-ci.org/ameer1234567890/gardenr.svg?branch=master)](https://travis-ci.org/ameer1234567890/gardenr)

# Gardenr
An indoor gardening assistant

#### How it works
* When `./gardenr.py` is run, it reads temperature, humidity and soil moisture level.
* It then updates these values to `./www/data.json` for later use by web frontend.
* It then updates the 15x2 LCD with the current time and soil moisture level.
* A preset moisture threshold is compared against the moisture level, and a notification is sent via IFTTT if soil is drier than the threshold.
* A python web server is then run with root `./www/`.
* The resulting frontend uses Javascript to query updated sensor data using AJAX.
* Now, all the collected data can be accessed by reaching `https://localhost` or Raspberry Pi's hostname.
* I use a the domain name `gardenr.ameer.io` which is signed with a LetsEncrypt certificate.
* Since https is used, the resulting frontend is a fully compliant Progressive Web App (PWA).
* The notification threshold can be changed from web interface.
* `./gardenr.py` can be made to run on startup, by installing systemd unit file `./gardenr.service`.
* Note: `./testdht.py`, `./testsht.py` `./testlcd.py` and `./testmoisture.py` are test scripts which are used for testing individual sensors.

#### TODO
* Fabricate improved PCB.

#### Components Used
* Raspberry Pi 3B+
* DHT22
* Soil Moisture Sensor KY70
* Analog to Digital Converter (ADC) YL-40
* 15x2 I2C LCD with PCF8574 as driver

#### Pinout for DHT22
```
Raspberry Pi  -  DHT22
-----------------------------
5V            -  VCC (Pin 1)
GND           -  GND (Pin 4)
GPIO4         -  DATA (Pin 2)
```

#### Pinout for Soil Moisture Sensor KY70
```
Raspberry Pi  -  Soil Moisture Sensor KY70
------------------------------------------
5V            -  VCC
GND           -  GND

ADC YL-40  -  Soil Moisture Sensor KY70
------------------------------------------
AIN3       -  A0
```

#### Pinout for ADC YL-40
```
Raspberry Pi  -  ADC YL-40
--------------------------
3.3V          -  VCC
GND           -  GND
SDA           -  SDA
SCL           -  SCL
```

#### Pinout for 15x2 I2C LCD
```
Raspberry Pi  -  15x2 I2C LCD
-----------------------------
5V            -  VCC
GND           -  GND
SDA           -  SDA
SCL           -  SCL
```

#### Libraries used
* smbus: https://github.com/pimoroni/py-smbus
* Adafruit-DHT: https://github.com/adafruit/Adafruit_Python_DHT
* I2C_LCD_driver: https://gist.github.com/DenisFromHR/cc863375a6e19dce359d

#### Pictures
* https://photos.app.goo.gl/o9qVq5qyfEnjEZFn7

#### Credits
* [Soil Moisture Sensor (Raspberry Pi)](https://www.instructables.com/id/Soil-Moisture-Sensor-Raspberry-Pi/)
* [How To Setup an I2C LCD on the Raspberry Pi](http://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/)
* [Measuring Voltage with Raspberry Pi](http://www.diyblueprints.net/measuring-voltage-with-raspberry-pi/)

#### Make Raspberry Pi's root filesystem read-only
* This is an optional step, which woul reduce chances of filesystem corruption due to improper shutdowns
* Use code and guide at: https://github.com/janztec/empc-arpi-linux-readonly
* Add below to `/etc/profile.d/motd.sh`
```shell
if grep -qs 'overlay=yes' /proc/cmdline; then
  textred=$(tput setaf 3)
  cat <<END_HEREDOC

${textred}==>WARNING: Root filesystem is read only.
None of the changes you make will be preserved after reboot.
To disable read only mode change 'overlay=yes' to 'overlay=no'
at kernel commandline.
END_HEREDOC
fi
```