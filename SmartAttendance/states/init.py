import json
import time
from states.state import AbstractState
from states.factory_reset import FactoryReset
from states.connect_to_wifi import ConnectToWiFi
from states.error import Error
from states.configure import Configure

from machine import Pin
from states.access_point import AccessPoint
FACTORY_RESET_INTERVAL = 5
class Init(AbstractState):
    def __init__(self, device):
        self.device = device
        self.is_reboot = False

    def exec(self):
        print('Initialization...')
        self.device.buzzer.stop()
        self.device.set_status_color((0, 0, 1023), "Initializing...")
        self.is_reboot = self.is_button_pressed()

        if not self.is_reboot:
            status = self.load_config_file()
            if not status:
                print("Unable to read config file.")
                self.device.set_status_color((1023, 0, 0), "Config Error")
                self.device.change_state(Error(self.device))
                return

            if not self.device.config.get("wifi") or \
               not self.device.config["wifi"].get("connection_data") or \
               not self.device.config["wifi"]["connection_data"].get("ssid") or \
               not self.device.config["wifi"]["connection_data"].get("password"):
                print("No Wi-Fi configuration found or it is invalid.")
                self.device.set_status_color((1023, 1023, 0), "Starting AP mode...")
                self.device.change_state(AccessPoint(self.device))
                return

            print("Switching to Wifi state...")
            self.device.set_status_color((0, 1023, 0))
            self.device.change_state(ConnectToWiFi(self.device))
        else:
            self.device.set_status_color((1023, 1023, 0), "Factory Reset...")
            self.device.change_state(FactoryReset(self.device))


    def load_config_file(self):
        try:
            with open("../config.json", "r") as config_file:
                self.device.config = json.load(config_file)
                print("Config data loaded:", self.device.config)
                return True
        except Exception as e:
            print(f"Error loading config file: {e}")
            return False

    def is_button_pressed(self):
        button = self.device.button
        start_time = time.time()
        while not button.value():
            if time.time() - start_time >= FACTORY_RESET_INTERVAL:
                print("Button held for 5 seconds, going to Factory Reset...")
                return True
            time.sleep(0.1)
        return False

