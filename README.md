# Gardenr
An indoor gardening assistant

#### How it works
* When `./gardenr.py` is run, it reads temperature, humidity and soil moisture level.
* It then updates these values to `./www/data.json` for later use by web frontend.
* It then updates the 15x2 LCD with the current time and soil moisture level.
* A python web server is then run with root `./www/`.
* The resulting frontend uses Javascript to query updated sensor data using AJAX.
* Now, all the collected data can be accessed by reaching `https://localhost` or Raspberry Pi's hostname.
* I use a self generated root CA which is installed on my devices.
* A certificate is generated by the root CA, for the Raspberry Pi.
* Since https is used, the resulting frontend is an fully compliant Progressive Web App (PWA).
* `./gardenr.py` can be made to run on startup, by running `sudo ./install-service`.
* Startup can be disabled by running `sudo ./uninstall-service`.
* Note: `./testdht.py`, `./testlcd.py` and `./testmoisture.py` are test scripts which are used for testing individual sensors.

#### TODO
* Polish web frontend.
* Make a PCB to accomodate all sensors and the ADC.
* Implement notifications (IFTTT?) when moisture level goes below a limit.

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
* I2C_LCD_driver: http://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/

#### Credits
* Soil Moisture Sensor (Raspberry Pi): https://www.instructables.com/id/Soil-Moisture-Sensor-Raspberry-Pi/
* How To Setup an I2C LCD on the Raspberry Pi: http://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/
* Measuring Voltage with Raspberry Pi: http://www.diyblueprints.net/measuring-voltage-with-raspberry-pi/
