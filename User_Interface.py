from Modules import *


class UserInput(QThread):

    user_to_manager_carrier = Signal(str)

    def __init__(self):
        super(UserInput, self).__init__()
        self.command = ''
        self.start()

    def run(self):
        while True:
            time.sleep(0.0001)
            self.command = str(input(''))
            self.user_to_manager_carrier.emit(self.command)
