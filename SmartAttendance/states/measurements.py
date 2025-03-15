from states.abstract_state import AbstractState
import time
import json  

MEASUREMENTS_FILE = "measurements.json"

class Measurements(AbstractState):
    def __init__(self, device):
        self.device = device
    
    def exec(self):
        print("Measuring temp...")
        temperature, humidity = self.read_sensor()
        
        if temperature is not None and humidity is not None:
            print(f"Measured temperature: {temperature}°C, humidity: {humidity}%")
            self.save_measurement(temperature, humidity)
        else:
            print("Measurement failed.")

    def read_sensor(self):
        try:
            self.device.sensor.measure()
            temperature = self.device.sensor.temperature()
            humidity = self.device.sensor.humidity()
            return temperature, humidity
        except OSError as e:
            print(f"Failed to read sensor: {e}")
            return None, None

    def save_measurement(self, temperature, humidity):
        timestamp = time.time()
        measurement = {
            "dt": 1234567890,
            "battery": 100,
            "tags": {},
            "metrics":{
                "temperature":[],
                "humidity":[]
                }
        }
        self.save_to_file(measurement)

    def save_to_file(self, data):
        try:
            with open(MEASUREMENTS_FILE, 'r') as f:
                measurements = json.load(f)
        except (OSError, ValueError):
            measurements = []

        measurements.append(data)

        with open(MEASUREMENTS_FILE, 'w') as f:
            json.dump(measurements, f)
