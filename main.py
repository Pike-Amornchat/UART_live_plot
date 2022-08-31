from Modules import *
from PySerial_RX import *
from User_Interface import *
from Data_Manager import *


class Application(QThread):

    def __init__(self):

        super(Application, self).__init__()

        # Setup QT base functions
        os.environ["QT_DEBUG_PLUGINS"] = "0"
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        # Other setup - will trust the internet
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        # Initialize PySerial connection
        self.UART_Connection = UART_RX(port=Config.port, baud_rate=Config.baud_rate, buffer_size=Config.buffer_size)
        self.UserInputThread = UserInput()
        self.Data_Manager = Data_Manager(serial_connection=self.UART_Connection,user_connection=self.UserInputThread)

        # Define the plot
        print('finished init')

        # We have created objects, but we haven't started running so this tells it to start
        self.app.processEvents()
        self.app.exec()


if __name__ == '__main__':
    sys.exit(Application())
