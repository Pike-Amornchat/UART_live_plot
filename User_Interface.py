from Modules import *


class UserInput(QThread):

    user_to_manager_carrier = Signal(str)

    def __init__(self):
        super(UserInput, self).__init__()
        self.command = ''
        self.start()

    def reset(self):
        self.terminate()
        self.command = ''
        self.start(priority=QThread.TimeCriticalPriority)

    def run(self):
        # return
        while True:
            self.command = str(input(''))
            self.user_to_manager_carrier.emit(self.command)
