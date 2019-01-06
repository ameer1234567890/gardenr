#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-

import I2C_LCD_driver

my_lcd = I2C_LCD_driver.lcd()
my_lcd.lcd_display_string('Hello World', 1, 0)
