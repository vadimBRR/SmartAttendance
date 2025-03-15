from machine import Pin, reset
from umqtt.simple import MQTTClient
from states.init import Init
from utils.rgb_controller import RGBController
from utils.buzzer_controller import BuzzerController

import json
import utime


class Device:
    def __init__(self):
        self.config = {}
        self.light = RGBController(red_pin=13, green_pin=12, blue_pin=11)
        self.button = Pin(10, Pin.IN, Pin.PULL_UP)
        self.mqtt = None
        self.state = Init(self)
        self.status_topic = None  
        self.button_hold_start = None
        self.block_scanning = False
        self.is_sleeping = False
        self.is_first_render = True
        self.buzzer = BuzzerController(pin=27)

    def setup_mqtt(self):
        try:
            config = self.config['mqtt']
            self.status_topic = f"{config['base_topic']}/status" 
            
            self.mqtt = MQTTClient(
                client_id=config['client_id'],
                server=config['server'], 
                port=config['port'],
                user=config['user'],
                password=config['password'],
                keepalive=30
            )
            last_will_message = json.dumps({
                "status": "offline",
                "timestamp": utime.time()
            })
            self.mqtt.set_last_will(
                topic=self.status_topic,
                msg=last_will_message,
                retain=True
            )
            self.mqtt.set_callback(self.on_message)
            self.mqtt.connect()
            self.mqtt.subscribe(f"{config['base_topic']}/config")  
            self.mqtt.subscribe(f"{config['base_topic']}/command") 
            print(f"Subscribed to: {config['base_topic']}/config and {config['base_topic']}/command")
            self.publish_status("online")
        except Exception as e:
            print(f"Error setting up MQTT: {e}")
            self.mqtt = None


    def on_message(self, topic, message):
        print(f"Global MQTT message received. Topic: {topic}, Message: {message}")
        if topic == b'gw/404_beta/config':  
            print("CONFIG")
            try:
                new_config = json.loads(message)
                if "current_class" in new_config:
                    self.config["current_class"] = new_config["current_class"].lower()
                    print(f"Current class updated to: {self.config['current_class']}")

                    data = [
                        ("abydoss", "147.232.52.251"),
                        ("caprica", "147.232.44.166"),
                        ("dune", "147.232.45.9"),
                        ("endor", "147.232.52.253"),
                        ("hyperion", "147.232.52.252"),
                        ("kronos", "147.232.44.94"),
                        ("meridian", "147.232.22.230"),
                        ("romulus", "147.232.22.242"),
                        ("solaris", "147.232.34.94"),
                        ("vulkan", "147.232.34.254")
                    ]
                    
                    for class_name, ip in data:
                        if class_name == self.config["current_class"]:
                            print(f"Setting MQTT server IP to: {ip}")
#                             self.config["mqtt"]["server"] = ip  
#                             self.save_config()
#                             self.reconnect_mqtt()
                            break
                        else:
                            print("blabla")
                    else:
                        print(f"Class {self.config['current_class']} not found in the data array.")
                    
                else:
                    print("Invalid config format: Missing 'current_class'")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in MQTT message.")
            except Exception as e:
                print(f"Error processing MQTT message: {e}")

        elif topic == b'gw/404_beta/command':  
            command = message.decode('utf-8').strip().lower()
            if command == "sleep":
                self.enter_sleep_mode()
            elif command == "wake_up":
                self.exit_sleep_mode()


    def enter_sleep_mode(self):
        print("Entering sleep mode...")
        self.is_sleeping = True
        self.publish_status("sleep")
        self.set_status_color((160, 32, 240))
        utime.sleep(1)
        self.set_status_color((0, 0, 0))

        

    def exit_sleep_mode(self):
        print("Exiting sleep mode...")
        self.is_sleeping = False
        self.publish_status("online")
        self.set_status_color((0, 1023, 0), "Waking up...")  
        self.change_state(Init(self))  

    def play_buzzer(self, frequency, duration):
        self.buzzer.play_tone(frequency, duration)

    def set_status_color(self, color, message=""):
        self.light.set_color(*color)
        

    def publish_status(self, status):
        try:
            if self.mqtt:
                timestamp = utime.time()
                message = {
                    "status": status,
                    "timestamp": timestamp
                }
                self.mqtt.publish(self.status_topic, json.dumps(message), retain=True)
                
        except Exception as e:
            print(f"Failed to publish status: {e}")

    def save_config(self):
        try:
            with open("../config.json", "w") as config_file:
                json.dump(self.config, config_file)
            print("Configuration saved successfully.")
        except Exception as e:
            print(f"Failed to save configuration: {e}")

    def check_button_hold(self):
        if self.button.value() == 0:
            if self.button_hold_start is None:
                self.button_hold_start = utime.ticks_ms()
                self.block_scanning = True
                self.set_status_color((1023, 0, 0))
            elif utime.ticks_diff(utime.ticks_ms(), self.button_hold_start) >= 5000:
                self.set_status_color((1023, 0, 0))
                utime.sleep(1)
                reset()
        else:
            self.button_hold_start = None
            self.block_scanning = False
            self.set_status_color((0, 0, 0))

    def change_state(self, state):
        self.state = state

    def disconnect_mqtt(self, final_disconnect=False):
        try:
            if final_disconnect:
                self.publish_status("offline")
            if self.mqtt:
                self.mqtt.disconnect()
        except Exception as e:
            print(f"Failed to disconnect MQTT: {e}")

    def run(self):
        self.buzzer.stop()
        self.running = True
        while self.running:
            if self.mqtt and self.mqtt.sock:
                try:
                    self.mqtt.check_msg()
                except OSError as e:
                    self.reconnect_mqtt()
            self.check_button_hold()

            if self.is_sleeping:
                utime.sleep(1)  
                continue

            if not self.block_scanning:
                self.state.exec()

            utime.sleep(0.1)

    def cleanup(self):
        self.light.off()
        self.buzzer.stop()
        self.disconnect_mqtt(final_disconnect=True)

    def reconnect_mqtt(self):
        try:
            if self.mqtt and self.mqtt.sock:
                self.mqtt.disconnect()
            new_client_id = f"{self.config['mqtt']['client_id']}_{utime.time()}"
            self.mqtt = MQTTClient(
                client_id=new_client_id,
                server=self.config['mqtt']['server'],
                port=self.config['mqtt']['port'],
                user=self.config['mqtt']['user'],
                password=self.config['mqtt']['password'],
                keepalive=30
            )
            self.setup_mqtt()
        except Exception as e:
            utime.sleep(5)

