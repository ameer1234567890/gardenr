#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-

import sht21
import time

SHT21 = sht21.SHT21()

while True:
    try:
        temperature, humidity = SHT21.measure(1)
        print("Temperature: %s °C  Humidity: %s %%" % (temperature, humidity))
    except:  # noqa: B001
        print("SHT21 I/O Error")
    time.sleep(2)
