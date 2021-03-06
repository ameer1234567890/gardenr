#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-
# Lifted from:
# http://www.diyblueprints.net/measuring-voltage-with-raspberry-pi/

import smbus
import time

# I2C-address of YL-40 PFC8591
address = 0x48

# Create I2C instance and open the bus
PFC8591 = smbus.SMBus(1)

# Configure PFC8591: Set channel to AIN3 | = i2cset -y 1 0x48 0x03
PFC8591.write_byte(address, 0x03)

# Print value
while True:
    Voltage_8bit = PFC8591.read_byte(address)  # = i2cget -y 1 0x48
    # convert 8 bit number to voltage 16.5/256
    # 16.5V max voltage for 0xff (=3.3V analog output signal)
    Voltage = Voltage_8bit * 0.064453125
    print(Voltage)
    time.sleep(1)
