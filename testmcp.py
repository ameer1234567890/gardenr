#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-

import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


while True:
    print(mcp.read_adc(1))
    time.sleep(0.5)
