from states.abstract_state import AbstractState
from states.error import Error
import dht
import machine
import time

class SelfTest(AbstractState):
    def __init__(self, device):
        self.device = device
        self.led = device.light # LED pre test svetla
        #self.sensor = dht.DHT22(machine.Pin(15))  # DHT22 senzor pripojený na GPIO 15
        self.error_code = None
    
    def exec(self):
        print("Running self-tests...")
        
        
        self.test_light()
        
       
        sensor_passed = self.test_sensor()
        
        if not sensor_passed:
            
            print("Sensor test failed!")
            self.device.error_code = 1 
            self.device.change_state(Error(self.device))  
        else:
            print("All tests passed.")
            
            self.device.change_state(Measurement(self.device))
    
    def test_light(self):
        print("Testing light...")
        self.led.on()
        time.sleep(0.5)
        self.led.off()
        print("Light test passed.")
    
    def test_sensor(self):
        print("Testing DHT sensor...")
        """try:
            self.sensor.measure()
            temperature = self.sensor.temperature()
            humidity = self.sensor.humidity()
            
            print(f"Measured temperature: {temperature}°C, humidity: {humidity}%")
            
            # Overenie rozsahu teploty a vlhkosti
            if 0 <= temperature <= 50 and 20 <= humidity <= 90:
                print("Sensor values within valid range.")
                return True
            else:
                print("Sensor values out of range!")
                return False
        except OSError as e:
            print(f"Sensor test failed: {e}")
            return False"""
