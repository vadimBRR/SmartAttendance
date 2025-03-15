from states.state import AbstractState
from machine import Pin
import neopixel
import time
import utime
import network
import sys
from machine import reset

class Error(AbstractState):
    def __init__(self, device):
        self.device = device
        self.led = self.device.light
        self.led_pin = 28  
        self.num_leds = 1  
        try:
            self.np = neopixel.NeoPixel(Pin(self.led_pin, Pin.OUT), self.num_leds)
        except Exception as e:
            print(f"Error initializing NeoPixel: {e}")
            self.np = None

    def exec(self):
        print("Entering Error state.")
        self.device.set_status_color((1023, 0, 0), "Error state:\nRestarting...")
        self.notify_error()
        try:
            self.set_color(0, 255, 0, 0)
            utime.sleep(1)
            self.set_color(0, 0, 0, 0)
        except Exception as e:
            print(f"Error setting NeoPixel color: {e}")

        try:
            wlan = network.WLAN(network.STA_IF)
            if wlan.active():
                wlan.disconnect()
                wlan.deinit()
        except Exception as e:
            print(f"Error managing Wi-Fi: {e}")

        print("Rebooting device...")
        try:
            reset()
        except Exception as e:
            print(f"Error during reset: {e}")


    def set_color(self, index, red, green, blue):
        if self.np is None:
            print("NeoPixel not initialized. Skipping set_color.")
            return
        try:
            self.np[index] = (red, green, blue)
            self.np.write()
        except Exception as e:
            print(f"Error setting color on NeoPixel: {e}")
