#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-

import Adafruit_DHT
import time

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

dht_humidity, dht_temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
print('DHT Temperature: ' + dht_temp + '°C DHT Humidity: ' + dht_humidity + '%'
#print('DHT Temperature: {0:0.1f}°C DHT Humidity: {1:0.1f}%'.format(dht_temp, dht_humidity))
time.sleep(1)
