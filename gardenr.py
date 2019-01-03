#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-
"""An indoor gardening assistant"""

import os
import ssl
import time
import json
import smbus
import datetime
import http.server
import socketserver
import Adafruit_DHT
import I2C_LCD_driver
import multiprocessing

PORT = 443
PID_FILE = '/tmp/gardenr.pid'
UPDATE_FILE = '/home/pi/gardenr/www/data.json'
UPDATE_INTERVAL = 10  # Update every 10 seconds
ADC_ADDRESS = 0x48
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
data = {}

PFC8591 = smbus.SMBus(1)
PFC8591.write_byte(ADC_ADDRESS, 0x03)  # set channel to AIN3 | = i2cset -y 1 0x48 0x03


def run_server():
    web_dir = os.path.join(os.path.dirname(__file__), 'www')
    os.chdir(web_dir)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(('', PORT), Handler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='/home/pi/tls/device.pem',
                                    server_side=True)
    print(datetime.datetime.now(), 'Running server at port', PORT)
    httpd.serve_forever()


def get_moisture():
    moisture_8bit = PFC8591.read_byte(ADC_ADDRESS)  # = i2cget -y 1 0x48
    moisture_8bit = PFC8591.read_byte(ADC_ADDRESS)  # Read twice since first read is "cached"
    moisture = moisture_8bit * 0.064453125  # convert 8 bit number to moisture 16.5/256 | 16.5V max voltage for 0xff (=3.3V analog output signal)
    return moisture


def get_temperature_and_humidity():
    return Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

def update_data():
    while True:
        print(datetime.datetime.now(), 'Updating data...')
        data['updated'] = str(time.time())
        data['moisture'] = str(get_moisture() * 10)
        humidity, temperature = get_temperature_and_humidity()
        data['temperature'] = str(temperature)
        data['humidity'] = str(humidity)
        json_data = json.dumps(data)
        with open(UPDATE_FILE, 'w') as fh:
            fh.write(json_data)
        update_screen()
        time.sleep(UPDATE_INTERVAL)


def update_screen():
    print(datetime.datetime.now(), 'Updating screen...')
    updated_time = str(datetime.datetime.fromtimestamp(float(data['updated'])).strftime('%Y-%m-%d %H:%M:%S'))
    moisture = get_moisture()
    moisture_lcd = 'MOISTURE:' + str(moisture * 10)
    my_lcd = I2C_LCD_driver.lcd()
    my_lcd.lcd_display_string(updated_time, 1, 0)
    my_lcd.lcd_display_string(moisture_lcd, 2, 0)


if __name__ == '__main__':
    try:
        with open(PID_FILE, 'w') as fh:
            fh.write(str(os.getpid()))
        run_server_thread = multiprocessing.Process(target=run_server)
        run_server_thread.start()
        update_data_thread = multiprocessing.Process(target=update_data)
        update_data_thread.start()
    except:
        run_server_thread.terminate()
        update_data_thread.terminate()
        os.remove(PID_FILE)
        print('PID file removed!')
