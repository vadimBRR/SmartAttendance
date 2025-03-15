from states.abstract_state import AbstractState
import machine

class FactoryReset(AbstractState):
    def __init__(self, device):
        self.device = device
    
    def exec(self):
        print('Reseting...')
        machine.reset()
