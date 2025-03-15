from states.publish_data import PublishData
from states.state import AbstractState
from states.error import Error
from states.configure import Configure

import time
import network
import ntptime
from machine import RTC
import utime


class ConnectToWiFi(AbstractState):
    
    def __init__(self, device, max_retries=3):
        self.device = device
        self.connection_time = self.device.config["wifi"]["connection_time"]
        self.connection_data = self.device.config["wifi"]["connection_data"]
        self.max_retries = max_retries 
    
    def _do_connect(self, ssid, password):
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('Connecting to network...')
            sta_if.active(True)
            sta_if.connect(ssid, password)
            start_time = utime.time()
            while not sta_if.isconnected():
                if utime.time() - start_time > self.connection_time:
                    print("Connection attempt timed out.")
                    return False
        print('Network config:', sta_if.ifconfig())
        return True
        
    def sync_time(self):

        try:
            ntptime.host = 'pool.ntp.org'
            ntptime.settime()
            print("Time synchronized:", RTC().datetime())
            return True
        except Exception as e:
            print("Failed to sync time:", e)
            return False
    
    def exec(self):
        print('Connecting to WiFi...')
        self.device.buzzer.stop()
        self.device.set_status_color((255, 100, 0))

        retries = 0
        

        while retries < self.max_retries:

            self.device.buzzer.stop()
            if self._do_connect(self.connection_data['ssid'], self.connection_data['password']):
                print("Connected to WiFi. Attempting to synchronize time...")
                if self.sync_time():
                    print("Time synchronized successfully.")
                    self.device.setup_mqtt()
#                     print("Switching to Configure state...")
                    self.device.change_state(Configure(self.device))
                    return
                else:
                    print("Sync time failed. Retrying WiFi connection...")
                    retries += 1
                    utime.sleep(3)  
            else:
                print(f"WiFi connection failed. Retrying ({retries + 1}/{self.max_retries})...")
                
                retries += 1
                utime.sleep(5)  

        print("Unable to connect to WiFi or sync time after multiple attempts.")
        self.handle_failure()



    def handle_failure(self):

        from states.access_point import AccessPoint
        self.device.change_state(AccessPoint(self.device))

