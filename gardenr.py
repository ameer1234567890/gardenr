#!/usr/bin/sudo env/bin/python3
# *-* coding: utf-8 -*-
"""An indoor gardening assistant"""

import http.server
import socketserver
import ssl
import os

PORT = 8000

web_dir = os.path.join(os.path.dirname(__file__), 'www')
os.chdir(web_dir)

Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile='../tls/device.pem',
                                   server_side=True)
print("serving at port", PORT)
httpd.serve_forever()
