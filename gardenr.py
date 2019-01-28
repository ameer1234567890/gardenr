#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-
"""An indoor gardening assistant"""


import os
import ssl
import time
import json
import smbus
import sht21
import datetime
import requests
import http.server
import socketserver
import urllib.parse
import Adafruit_DHT
import I2C_LCD_driver
import multiprocessing


PORT = 443
PID_FILE = '/tmp/gardenr.pid'
UPDATE_FILE = './www/data.json'
UPDATE_INTERVAL = 10  # Update every 10 seconds
ADC_ADDRESS = 0x48
DHT_SENSOR = Adafruit_DHT.DHT22
PFC8591 = smbus.SMBus(1)
SHT21 = sht21.SHT21()
DHT_PIN = 4
URL = 'https://gardenr.ameer.io'
NOTIFY_FILE = '/boot/gardenr/notify.log'  # Since /dev/root is RO
CONFIG_FILE = '/boot/gardenr/config.json'  # Since /dev/root is RO
data = {}
ifttt_key = ''
thingspeak_key = ''
notify_moisture_level = ''
moisture = 0
temperature = 0
humidity = 0
upload_counter = 0


if not os.path.isfile(NOTIFY_FILE):
    with open(NOTIFY_FILE, 'w') as fh:
        fh.write('NO')


# set channel to AIN3 | = i2cset -y 1 0x48 0x03
PFC8591.write_byte(ADC_ADDRESS, 0x03)


def check_config_file():
    if not os.path.isfile(CONFIG_FILE):
        write_config()
        print(datetime.datetime.now(), 'New config file created!')


def read_config():
    global ifttt_key
    global thingspeak_key
    global notify_moisture_level
    with open(CONFIG_FILE) as fh:
        config = json.load(fh)
    ifttt_key = config['IFTTT_KEY']
    thingspeak_key = config['THINGSPEAK_KEY']
    notify_moisture_level = config['NOTIFY_MOISTURE_LEVEL']


def write_config(c_ifttt_key='NONE', c_thingspeak_key='NONE',
                 c_notify_moisture_level='0'):
    config = {}
    config['IFTTT_KEY'] = c_ifttt_key
    config['THINGSPEAK_KEY'] = c_thingspeak_key
    config['NOTIFY_MOISTURE_LEVEL'] = c_notify_moisture_level
    with open(CONFIG_FILE, 'w') as fh:
        json.dump(config, fh)


class HTTPSHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        global notify_moisture_level
        if self.path == '/set-threshold':
            length = int(self.headers.get('content-length'))
            field_data = self.rfile.read(length)
            fields = urllib.parse.parse_qs(field_data)
            threshold_field = fields.get(b'threshold')
            if threshold_field is not None:
                threshold = str(threshold_field).split('\'')[1]
                if isinstance(int(threshold), int):
                    write_config(c_notify_moisture_level=threshold)
                    notify_moisture_level = threshold
                    print(datetime.datetime.now(),
                          'Notify threshold set to {}'
                          .format(notify_moisture_level))
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write('Posted'.encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('Bad Request!'.encode('utf-8'))

    def do_GET(self):  # noqa: N802
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


class HTTPRedirect(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        print(self.path)
        self.send_response(301)
        new_path = '%s%s' % (URL, self.path)
        self.send_header('Location', new_path)
        self.end_headers()


def run_server():
    web_dir = os.path.join(os.path.dirname(__file__), 'www')
    os.chdir(web_dir)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(('', PORT), HTTPSHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   certfile='/home/pi/tls/device.pem',
                                   server_side=True)
    print(datetime.datetime.now(), 'Running server at port', PORT)
    httpd.serve_forever()


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
    # return temperature, humidity = SHT21.measure(1)


def notify_moisture(moisture):
    global notify_moisture_level
    if int(notify_moisture_level) != 0 and ifttt_key:
        if moisture > int(notify_moisture_level):
            with open(NOTIFY_FILE, 'r') as fh:
                notified = str(fh.read())
            if notified == 'NO':
                print(datetime.datetime.now(),
                      'Low moisture ({})! Notifying...'
                      .format(moisture))
                maker_url = 'https://maker.ifttt.com/trigger/' + \
                            'soil_moisture/with/key/'
                maker_url = maker_url + ifttt_key
                maker_url = maker_url + '?value1=' + str(moisture)
                r = requests.get(maker_url)
                print(r.text)
                with open(NOTIFY_FILE, 'w') as fh:
                    fh.write('YES')
            else:
                print(datetime.datetime.now(),
                      'Low moisture ({})! Notified already!'
                      .format(moisture))
        else:
            with open(NOTIFY_FILE, 'w') as fh:
                fh.write('NO')


def update_data():
    global notify_moisture_level
    global upload_counter
    global moisture
    global temperature
    global humidity
    while True:
        print('')  # Nicer logs
        print(datetime.datetime.now(), 'Updating data...')
        read_config()
        moisture = get_moisture() * 10
        data['updated'] = str(time.time())
        data['moisture'] = str(moisture)
        humidity, temperature = get_temperature_and_humidity()
        data['temperature'] = str(temperature)
        data['humidity'] = str(humidity)
        data['threshold'] = str(notify_moisture_level)
        json_data = json.dumps(data)
        with open(UPDATE_FILE, 'w') as fh:
            fh.write(json_data)
        multiprocessing.Process(target=update_screen, args=(moisture,)).start()
        multiprocessing.Process(target=notify_moisture, args=(moisture,)) \
                       .start()
        # Upload to Thingspeak only once in every 2 runs (20 seconds)
        # to follow Thingspeak's API limits.
        upload_counter += 1
        if upload_counter == 1:
            multiprocessing.Process(target=upload_data,
                                    args=(moisture, temperature, humidity,)) \
                        .start()
        else:
            upload_counter = 0
        time.sleep(UPDATE_INTERVAL)


def update_screen(moisture):
    print(datetime.datetime.now(), 'Updating screen with moisture {}...'
          .format(moisture))
    updated_time = str(datetime.datetime.fromtimestamp(float(data['updated']))
                       .strftime('%Y-%m-%d %H:%M:%S'))
    moisture_lcd = 'MOISTURE:' + str(moisture)
    my_lcd = I2C_LCD_driver.lcd()
    my_lcd.lcd_display_string(updated_time, 1, 0)
    my_lcd.lcd_display_string(moisture_lcd, 2, 0)


def upload_data(moisture, temperature, humidity):
    print(datetime.datetime.now(), 'Uploading data to Thingspeak...')
    thingspeak_url = 'https://api.thingspeak.com/update?' + \
        'api_key=' + thingspeak_key + \
        '&field1=' + str(moisture) + \
        '&field2=' + str(temperature) + \
        '&field3=' + str(humidity)
    r = requests.get(thingspeak_url)
    print(datetime.datetime.now(), 'Thingspeak Response: {}'
          .format(r.text))


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
