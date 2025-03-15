class AbstractState:

    def __init__(self, device):
        self.device = device

    def on_enter(self):
        self.device.check=True

    def on_exit(self):
        self.device.check=False

    def exec(self):
        pass
