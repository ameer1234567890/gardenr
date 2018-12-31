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

PORT = 443
PID_FILE = '/tmp/gardenr.pid'
UPDATE_INTERVAL = 10  # Update every 10 seconds

def run_server():
    web_dir = os.path.join(os.path.dirname(__file__), 'www')
    os.chdir(web_dir)

    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(('', PORT), Handler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='/home/pi/tls/device.pem',
                                    server_side=True)
    print('Running server at port', PORT)
    httpd.serve_forever()


datetime.datetime.now()

if __name__ == '__main__':
    try:
        with open(PID_FILE, 'w') as fh:
            fh.write(str(os.getpid()))
        run_server_thread = multiprocessing.Process(target=crun_server)
        run_server_thread.start()
    except KeyboardInterrupt:
        httpd.server_close()
        run_server_thread.terminate()
        #GPIO.cleanup()
        #print('GPIO cleanup done!')
        os.remove(PID_FILE)
        print('PID file removed!')
