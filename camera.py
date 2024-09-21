import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import ssl
from abuseipdb_wrapper import AbuseIPDB
import subprocess, socket

import secrets

PAGE="""\
<html>
<head>
<title>GuineaPig Camera</title>
</head>
<body style="background-color:black;">
<center><h1 style="color:white;height=5%;">Guinea Pig Camera</h1></center>
<center><img src="stream.mjpg" width="95%" height="95%"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.request.settimeout(60) #Add timeout for the get requests
        ip = self.client_address[0]
        #check if IP is known
        if(whiteList.__contains__(ip)):
            pass
        else:
            # do check for malicious IP:
            abuseValues = abuse.check_ip(self.client_address[0])
            print(abuseValues)
            if(abuseValues['abuseConfidenceScore'] > 70):
                # enable UFW firewall for this IP
                subprocess.run(["sudo","ufw","deny","from",ip])
                print(f"added {ip} to blacklist")
                file = open("checks.txt","a")
                file.write(f"added {ip} to blacklist\n")
                file.close()
                return
            else:
                # add ip to whitelist if safe, this helps prevent repeated queries for this IP
                whiteList.append(ip)
                print(f"added {ip} to whitelist")
                file = open("checks.txt","a")
                file.write(f"added {ip} to whitelist\n")
                file.close()
        
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

#Start the abuse object
apiKey = abuse_API_Key
abuse = AbuseIPDB(API_KEY=apiKey)
whiteList = []
socket.setdefaulttimeout(30)
with picamera.PiCamera(resolution='1920x1080', framerate=24) as camera:
    output = StreamingOutput()
    camera.rotation = 180
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8082)
        server = StreamingServer(address, StreamingHandler)
        server.socket = ssl.wrap_socket(server.socket, keyfile=key_file_path, certfile=cert_file_path,server_side=True)
        print("started")
        server.serve_forever()
    finally:
        camera.stop_recording()
