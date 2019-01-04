# Gardenr
An indoor gardening assistant

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
