from states.state import AbstractState
from states.connect_to_wifi import ConnectToWiFi
import network
import socket
import json
from utils.url_parser import url_decode
from machine import reset
import time


class AccessPoint(AbstractState):
    def __init__(self, device, timeout=300):
        self.device = device
        self.ap = None
        self.timeout = timeout
        self.start_time = time.time()

    def scan_networks(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        networks = wlan.scan()
        wlan.active(False)
        return [(net[0].decode('utf-8'), net[3]) for net in networks]

    def generate_ssid_dropdown(self):
        networks = self.scan_networks()
        options = "".join(
            f'<option value="{ssid}">{ssid} (Signal: {signal})</option>'
            for ssid, signal in networks
        )
        return options

    def start_ap(self):
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid='PicoConfig', password='12345678')
        print('Access point started. Connect to Wi-Fi: PicoConfig')
        print('Open browser and go to http://192.168.4.1')

    def start_web_server(self):
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(1)
        print('Web server listening on http://192.168.4.1')

        while True:
            if time.time() - self.start_time > self.timeout:
                print("Access Point timed out. Restarting device...")
                s.close()
                self.ap.active(False)
                reset()

            try:
                cl, addr = s.accept()
                print('Client connected from', addr)

                try:
                    request = cl.recv(1024).decode('utf-8')
                    print('Request:', request)

                    if '/config?' in request:
                        params = request.split(' ')[1].split('?')[1]
                        params = params.split('&')

                        ssid = url_decode(params[0].split('=')[1])
                        password = url_decode(params[1].split('=')[1])

                        if not ssid:
                            cl.send('HTTP/1.0 400 Bad Request\r\nContent-type: text/html\r\n\r\n')
                            cl.send('<h1>Error: Please select a Wi-Fi network.</h1>')
                            cl.close()
                            continue

                        self.save_config(ssid, password)

                        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                        cl.send('<h1>Wi-Fi Configured! Connecting...</h1>')
                        cl.close()

                        s.close()
                        self.ap.active(False)
                        self.device.change_state(ConnectToWiFi(self.device))
                        return

                    html = f"""<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Configure Wi-Fi</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f4f4f9;
                                margin: 0;
                                padding: 0;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                            }}
                            .container {{
                                background: #ffffff;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                border-radius: 8px;
                                padding: 20px 30px;
                                width: 90%;
                                max-width: 400px;
                                text-align: center;
                            }}
                            h1 {{
                                color: #333;
                                margin-bottom: 20px;
                            }}
                            form {{
                                display: flex;
                                flex-direction: column;
                                align-items: stretch;
                            }}
                            select, input[type="password"] {{
                                font-size: 16px;
                                padding: 10px;
                                margin-bottom: 20px;
                                border: 1px solid #ccc;
                                border-radius: 4px;
                                width: 100%;
                                box-sizing: border-box;
                            }}
                            input[type="submit"] {{
                                font-size: 16px;
                                background-color: #4CAF50;
                                color: white;
                                border: none;
                                border-radius: 4px;
                                padding: 10px;
                                cursor: pointer;
                            }}
                            input[type="submit"]:hover {{
                                background-color: #45a049;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Configure Wi-Fi</h1>
                            <form action="/config" method="get">
                                <select name="ssid" required>
                                    <option value="" disabled selected>Select Wi-Fi Network</option>
                                    {self.generate_ssid_dropdown()}
                                </select>
                                <input type="password" name="password" placeholder="Password" required>
                                <input type="submit" value="Save">
                            </form>
                        </div>
                    </body>
                    </html>
                    """


                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                    cl.send(html)
                    cl.close()
                except OSError as e:
                    print(f"Client communication error: {e}")
                    cl.close()
            except OSError as e:
                print(f"Socket error: {e}")
                s.close()
                break

    def save_config(self, ssid, password):
        self.device.config['wifi'] = {
            'connection_data': {
                'ssid': ssid,
                'password': password
            },
            'connection_time': self.device.config.get('wifi', {}).get('connection_time', 6)
        }

        with open('config.json', 'w') as f:
            json.dump(self.device.config, f)
        print("Wi-Fi configuration saved!")

    def exec(self):
        print("Starting Access Point mode...")
        self.device.set_status_color((1023, 1023, 0), "AP Mode:\nSSID: PicoConfig\nPass: 12345678\nIP: 192.168.4.1")
        self.start_ap()
        self.start_web_server()

