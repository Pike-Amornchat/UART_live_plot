from Modules import *
from PySerial_RX import *


class Config:

    # Serial port config settings
    port = 'COM9'
    baud_rate = 115200
    buffer_size = 10000


class Application:

    def __init__(self):

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

        # Define the plot
        print('finished init')

        # We have created objects, but we haven't started running so this tells it to start
        self.app.processEvents()
        self.app.exec()


if __name__ == '__main__':
    sys.exit(Application())
