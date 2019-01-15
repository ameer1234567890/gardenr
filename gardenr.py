#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-
"""An indoor gardening assistant"""

# Setup config file at /home/pi/ifttt.conf.py as below:
# class Config():
#    IFTTT_KEY = 'YOUR_IFTTT_WEBHOOK_KEY_HERE'
#    NOTIFY_MOISTURE_LEVEL = 0  # Set to 0 to disable notifications


import os
import ssl
import time
import json
import smbus
import datetime
import requests
import http.server
import socketserver
import Adafruit_DHT
import I2C_LCD_driver
import multiprocessing


PORT = 443
PID_FILE = '/tmp/gardenr.pid'
UPDATE_FILE = './www/data.json'
UPDATE_INTERVAL = 10  # Update every 10 seconds
ADC_ADDRESS = 0x48
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
URL = 'https://gardenr.ameer.io'
NOTIFY_FILE = './notify.log'
CONFIG_FILE = './config.json'
data = {}
ifttt_key = ''
notify_moisture_level = ''


if not os.path.isfile(NOTIFY_FILE):
        with open(NOTIFY_FILE, 'w') as fh:
            fh.write('NO')


PFC8591 = smbus.SMBus(1)
# set channel to AIN3 | = i2cset -y 1 0x48 0x03
PFC8591.write_byte(ADC_ADDRESS, 0x03)


def check_config_file():
    if not os.path.isfile(CONFIG_FILE):
        write_config()
        print('New config file created!')


def read_config():
    global ifttt_key
    global notify_moisture_level
    with open(CONFIG_FILE) as fh:
        config = json.load(fh)
    ifttt_key = config['IFTTT_KEY']
    notify_moisture_level = config['NOTIFY_MOISTURE_LEVEL']


def write_config(c_ifttt_key='NONE', c_notify_moisture_level='0'):
    config = {}
    config['IFTTT_KEY'] = c_ifttt_key
    config['NOTIFY_MOISTURE_LEVEL'] = c_notify_moisture_level
    with open(CONFIG_FILE, 'w') as fh:
        json.dump(config, fh)


def run_server():
    web_dir = os.path.join(os.path.dirname(__file__), 'www')
    os.chdir(web_dir)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(('', PORT), handler)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   certfile='/home/pi/tls/device.pem',
                                   server_side=True)
    print(datetime.datetime.now(), 'Running server at port', PORT)
    httpd.serve_forever()


class HTTPRedirect(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        print(self.path)
        self.send_response(301)
        new_path = '%s%s' % (URL, self.path)
        self.send_header('Location', new_path)
        self.end_headers()


def run_http():
    # This is to redirect http to https
    socketserver.TCPServer(('', 80), HTTPRedirect).serve_forever()


def get_moisture():
    # = i2cget -y 1 0x48
    moisture_8bit = PFC8591.read_byte(ADC_ADDRESS)
    # Read twice since first read is "cached"
    moisture_8bit = PFC8591.read_byte(ADC_ADDRESS)
    # convert 8 bit number to moisture 16.5/256
    # 16.5V max voltage for 0xff (=3.3V analog output signal)
    moisture = moisture_8bit * 0.064453125
    return moisture


def get_temperature_and_humidity():
    return Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)


def notify_moisture(moisture):
    if Config.NOTIFY_MOISTURE_LEVEL != 0 and ifttt_key:  # noqa: F821
        if moisture > int(notify_moisture_level):
            with open(NOTIFY_FILE, 'r') as fh:
                notified = str(fh.read())
            if notified == 'NO':
                print('Low moisture level detected! Notifying...')
                maker_url = 'https://maker.ifttt.com/trigger/' + \
                            'soil_moisture/with/key/'
                maker_url = maker_url + ifttt_key  # noqa: F821
                maker_url = maker_url + '?value1=' + str(moisture)
                r = requests.get(maker_url)
                print(r.text)
                with open(NOTIFY_FILE, 'w') as fh:
                    fh.write('YES')
            else:
                print('Low moisture level detected! Notified already!')
        else:
            with open(NOTIFY_FILE, 'w') as fh:
                fh.write('NO')


def update_data():
    while True:
        print(datetime.datetime.now(), 'Updating data...')
        moisture = get_moisture() * 10
        data['updated'] = str(time.time())
        data['moisture'] = str(moisture)
        humidity, temperature = get_temperature_and_humidity()
        data['temperature'] = str(temperature)
        data['humidity'] = str(humidity)
        json_data = json.dumps(data)
        with open(UPDATE_FILE, 'w') as fh:
            fh.write(json_data)
        update_screen()
        notify_moisture(moisture)
        time.sleep(UPDATE_INTERVAL)


def update_screen():
    print(datetime.datetime.now(), 'Updating screen...')
    updated_time = str(datetime.datetime.fromtimestamp(float(data['updated']))
                       .strftime('%Y-%m-%d %H:%M:%S'))
    moisture = get_moisture()
    moisture_lcd = 'MOISTURE:' + str(moisture * 10)
    my_lcd = I2C_LCD_driver.lcd()
    my_lcd.lcd_display_string(updated_time, 1, 0)
    my_lcd.lcd_display_string(moisture_lcd, 2, 0)


if __name__ == '__main__':
    try:
        with open(PID_FILE, 'w') as fh:
            fh.write(str(os.getpid()))
        check_config_file()
        read_config()
        run_server_thread = multiprocessing.Process(target=run_server)
        run_server_thread.start()
        update_data_thread = multiprocessing.Process(target=update_data)
        update_data_thread.start()
        run_http_thread = multiprocessing.Process(target=run_http)
        run_http_thread.start()
    except:  # noqa: B001
        run_server_thread.terminate()
        update_data_thread.terminate()
        run_http_thread.terminate()
        os.remove(PID_FILE)
        print('PID file removed!')
