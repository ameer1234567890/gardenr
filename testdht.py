#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-

import Adafruit_DHT

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

dht_humidity, dht_temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
print('Temp: {} | Humidity: {}'.format(dht_temp, dht_humidity))
