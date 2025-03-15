from states.state import AbstractState
#from states.read import Reading
import time
import json
from states.mfrc522 import MFRC522
import utime

class Idle(AbstractState):
    def __init__(self, device):
        self.device = device

    def exec(self):
        print("Checking if class is set...")
        if not self.device.config.get("current_class"):
            print("Class not set. Waiting for configuration...")
            time.sleep(1)  
            return

        print("Waiting for card...")
        self.device.set_status_color((0, 0, 0)) 
        reader = MFRC522(spi_id=0, sck=6, miso=4, mosi=7, cs=5, rst=22)
        try:
            reader.init()
            (stat, tag_type) = reader.request(reader.REQALL)
            if stat == reader.OK:
                print("Card detected!")
                from states.read import Reading
                self.device.change_state(Reading(self.device, reader))
            else:
                print("No card detected. Retrying...")
        except OSError as e:
            print(f"Error reading card: {e}")


