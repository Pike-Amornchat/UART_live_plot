from Modules import *


class UserInput(QThread):

    user_to_manager_carrier = Signal(str)

    def __init__(self):
        super(UserInput, self).__init__()