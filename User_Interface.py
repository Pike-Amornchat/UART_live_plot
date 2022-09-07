from Modules import *


class UserInput(QThread):

    """
    This thread takes the user input and emits it to the data manager - needs to be thread because input() stops
    every other line in the thread from running.
    """

    # Set up signal connection to manager for emit
    user_to_manager_carrier = Signal(str)

    def __init__(self):

        # QT inherit all of QThread
        super(UserInput, self).__init__()

        # Stores the command inputted by user
        self.command = ''

        # This thread should be lowest priority because a user input does not have to be that fast
        self.start(priority = QThread.LowestPriority)

    def reset(self):

        """
        Resets the command buffer when caled by Data Manager
        :return: None
        """

        self.terminate()
        self.command = ''
        self.start()

    def run(self):

        """
        Run called by QThread start() and constantly receives user inputs, then emits to Data Manager
        :return:
        """

        # Infinite loop receiving command
        while True:

            # Get the input after pressing enter and emit
            self.command = str(input(''))
            self.user_to_manager_carrier.emit(self.command)
