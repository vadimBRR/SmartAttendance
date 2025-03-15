from states.state import AbstractState
from states.publish_data import PublishData
import time
import json
from states.mfrc522 import MFRC522
import utime

ATTENDANCES_FILE = "attendances.json"

class Reading(AbstractState):
    def __init__(self, device, reader):
        self.device = device
        self.reader = reader
        self.card = None

    def exec(self):
        print("Reading card...")
        if not self.device.config.get("current_class"):
            print("Class not set. Cannot proceed with reading.")
            from states.idle import Idle
            self.device.change_state(Idle(self.device))
            return

        if self.reader:
            (stat, uid) = self.reader.SelectTagSN()
            if stat == self.reader.OK:
                self.card = int.from_bytes(bytes(uid), "little", False)

            if self.card:   
                self.save_to_file()
                print("Attendance saved.")
                self.device.change_state(PublishData(self.device, {
                    "id": self.card,
                    "dt": utime.time(),
                    "class": self.device.config["current_class"]
                }))
            else:
                print("Failed to read card.")
                from states.idle import Idle
                self.device.change_state(Idle(self.device))

    def save_to_file(self):
        timestamp = utime.time()
        data = {
            "dt": timestamp,
            "id": self.card
        }
        
        try:
            with open(ATTENDANCES_FILE, "r") as f:
                attendances = json.load(f)
        except (OSError, ValueError):
            attendances = {"attendances": []}

        attendances["attendances"].append(data)

        with open(ATTENDANCES_FILE, "w") as f:
            json.dump(attendances, f)