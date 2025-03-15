from umqtt.simple import MQTTClient
import json
import time
from states.state import AbstractState
from states.idle import Idle
from states.error import Error


class Configure(AbstractState):
    def __init__(self, device):
        self.device = device
        self.is_config_updated = False

    def setup_mqtt(self):
        if not self.device.mqtt:
            self.device.setup_mqtt()

        try:
            self.device.mqtt.subscribe("kpi/endor/404_beta/config")
            print("Subscribed to config topic.")
        except Exception as e:
            print(f"Failed to subscribe to MQTT topics: {e}")
            self.device.change_state(Error(self.device))

    def on_message(self, topic, message):
        print(f"Message received on topic '{topic}': {message}")
        if topic == b'kpi/endor/404_beta/config':
            try:
                new_config = json.loads(message)
                if "current_class" in new_config:
                    self.update_class(new_config["current_class"])
                    self.is_config_updated = True
                else:
                    self.update_config(new_config)
            except json.JSONDecodeError:
                print("Invalid config format received.")

    def update_class(self, class_name):
        print(f"Updating current class to: {class_name}")
        self.device.config["current_class"] = class_name
        self.save_config()
        print(f"Current class updated to: {class_name}")

    def update_config(self, new_config):
        print("Updating device configuration...")
        self.device.config.update(new_config)
        self.save_config()
        print("Configuration updated successfully.")
    
    def is_config_set(self):
        current_class = self.device.config.get("current_class")
        return current_class is not None and current_class.strip() != ""

    def save_config(self):
        try:
            with open("../config.json", "w") as config_file:
                json.dump(self.device.config, config_file)
            print("Configuration saved to file.")
        except Exception as e:
            print(f"Failed to save configuration: {e}")

    def exec(self):
        print("Configuring device...")
#         self.setup_mqtt()
        if self.is_config_set():
            print("Configuration already set. Switching to Idle state.")
            
            print(self.device.is_first_render)
            if self.device.is_first_render == False:
                self.device.change_state(Idle(self.device))
                
                return
            else:
                self.device.enter_sleep_mode()
                self.device.is_first_render = False;
                return
            

        try:
            
            print("waiting...")
            self.device.mqtt.check_msg()  

            if self.is_config_set():
                print("Configuration updated. Exiting Configure state.")
                
                print(self.device.is_first_render)
                if self.device.is_first_render == False:
                    self.device.change_state(Idle(self.device))
                    return
                else:
                    self.device.enter_sleep_mode()
                    self.device.is_first_render = False;

                    return
            
            
            
            time.sleep(1)  
        except Exception as e:
            print(f"Error during MQTT listening: {e}")
            self.device.change_state(Error(self.device))

