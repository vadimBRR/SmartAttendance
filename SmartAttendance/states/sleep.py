from states.state import AbstractState
import utime
from states.idle import Idle

class Sleep(AbstractState):
    def __init__(self, device):
        self.device = device

    from states.state import AbstractState

class Sleep(AbstractState):
    def __init__(self, device):
        self.device = device

    def exec(self):
        print("Entering Sleep mode...")
        self.device.publish_status("sleeping")
        self.device.set_status_color((0, 0, 0), "Sleeping...")
        
        print("Sleep state is active. Waiting for 'wake_up' command...")

