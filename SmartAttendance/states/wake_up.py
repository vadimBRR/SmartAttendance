from states.self_tests import SelfTest
from states.init import Init
from states.state import AbstractState


class WakeUp(AbstractState):
    def exec(self):
        print("Wake up")
        self.device.change_state(Init(self.device))

