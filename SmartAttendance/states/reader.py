from states.state import AbstractState
import time
import json
from states.mfrc522 import MFRC522
import utime

MEASUREMENTS_FILE = "attendances.json"

class Attendances(AbstractState):
    def __init__(self, device):
        self.device = device
    
    def exec(self):
        print("Scanning...")
        card = self.read_isic()
        
        if card is not None:
            print("Scan was successful!")
            self.save_attendances(card)
            self.device.change_state(self)
        else:
            print("Failed to scan.")

    def read_isic(self):
        reader = MFRC522(spi_id=0, sck=6, miso=4, mosi=7, cs=5, rst=22)
        print("Bring TAG closer...")
        
        while True:
            try:
                reader.init()
                (stat, tag_type) = reader.request(reader.REQALL)
                if stat == reader.OK:
                    (stat, uid) = reader.SelectTagSN()
                    if stat == reader.OK:
                        card = int.from_bytes(bytes(uid), "little", False)
                        print(f"CARD ID: {card}")
                        return card
                else:
                    print("No card detected. Waiting...")
            except OSError as e:
                print(f"Failed to read card: {e}. Retrying...")
            
            utime.sleep(0.5) 

    def save_attendances(self, id):
        timestamp = utime.time()
        attendances = {
            "dt": timestamp,
            "id": id
        }
        self.save_to_file(attendances)

    def save_to_file(self, data):
        try:
            with open(MEASUREMENTS_FILE, "r") as f:
                attendances = json.load(f)
        except (OSError, ValueError):
            attendances = {"attendances": []}

        attendances["attendances"].append(data)

        with open(MEASUREMENTS_FILE, "w") as f:
            json.dump(attendances, f)
