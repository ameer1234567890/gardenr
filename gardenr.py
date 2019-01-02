#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-
"""An indoor gardening assistant"""

import http.server
import socketserver
import ssl
import time
import datetime
import multiprocessing
#import RPi.GPIO as GPIO
import os
import json
import I2C_LCD_driver

PORT = 443
PID_FILE = '/tmp/gardenr.pid'
UPDATE_FILE = '/home/pi/gardenr/www/data.json'
UPDATE_INTERVAL = 10  # Update every 10 seconds
data = {}
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(('', PORT), Handler)
my_lcd = I2C_LCD_driver.lcd()


def run_server():
    web_dir = os.path.join(os.path.dirname(__file__), 'www')
    os.chdir(web_dir)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='/home/pi/tls/device.pem',
                                    server_side=True)
    print('Running server at port', PORT)
    httpd.serve_forever()


def update_data():
    while True:
        print('Updating data...')
        data['updated'] = str(time.time())
        json_data = json.dumps(data)
        with open(UPDATE_FILE, 'w') as fh:
            fh.write(json_data)
        time.sleep(UPDATE_INTERVAL)
        update_screen()


def update_screen():
    print('Updating screen...')
    str_pad = ' ' * 16
    updated_time = str(datetime.datetime.fromtimestamp(float(data['updated'])).strftime('%Y-%m-%d %H:%M:%S'))
    soil_moisture = 'Moisture: N/A'
    my_lcd.lcd_display_string(updated_time, 1, 0)
    my_lcd.lcd_display_string(soil_moisture, 2, 0)
    """updated_time = str_pad + updated_time
    while True:
        for i in range (0, len(updated_time)):
            lcd_text = updated_time[i:(i+16)]
            my_lcd.lcd_display_string(lcd_text, 1)
            time.sleep(0.2)
            my_lcd.lcd_display_string(str_pad, 1)"""


if __name__ == '__main__':
    try:
        with open(PID_FILE, 'w') as fh:
            fh.write(str(os.getpid()))
        #run_server_thread = multiprocessing.Process(target=run_server)
        #run_server_thread.start()
        update_data_thread = multiprocessing.Process(target=update_data)
        update_data_thread.start()
    except:
        httpd.server_close()
        #run_server_thread.terminate()
        mylcd.lcd_clear()
        update_data_thread.terminate()
        #GPIO.cleanup()
        #print('GPIO cleanup done!')
        os.remove(PID_FILE)
        print('PID file removed!')
