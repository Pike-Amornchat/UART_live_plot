from Modules import *
from PySerial_RX import *
from User_Interface import *
from Data_Manager import *
from Raw_Processor import *


class Application(QThread):

    def __init__(self):

        """
        This is the main class, which does all of the initialisation and holds the other modules/threads.
        """

        # QT inherit all of QThread
        super(Application, self).__init__()

        # Setup QT base functions
        os.environ["QT_DEBUG_PLUGINS"] = "0"
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        # Other setup - will trust the internet
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        # Initialize PySerial connection (thread)
        self.UART_Connection = UART_RX(port=Config.port, baud_rate=Config.baud_rate, buffer_size=Config.buffer_size)

        # Initialize the user input thread (thread)
        self.UserInputThread = UserInput()

        # Initialize the data manager object (on/off thread) - the rest is initialized inside this class
        self.Data_Manager = Data_Manager(serial_connection=self.UART_Connection,
                                         user_connection=self.UserInputThread)

        # We have created objects, but we haven't started running so this tells it to start
        self.app.processEvents()
        self.app.exec()


# Call class here and run the application
if __name__ == '__main__':
    app = Application()
    sys.exit(app)
