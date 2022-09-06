from Modules import *


class UART_RX(QThread):

    serial_to_manager_carrier = Signal(str)

    def __init__(self, port='COM14', baud_rate=115200, buffer_size=10000):
        super(UART_RX, self).__init__()

        # Attributes for PySerial setup
        self.port = port
        self.baud_rate = baud_rate
        self.buffer_size = buffer_size
        self.UART_buffer = bytearray()

        self.now = time.time()

        # Initialize PySerial - specify baud rate
        self.serial_connection = serial.Serial()

        # Set the receive and transmit buffer size
        self.serial_connection.set_buffer_size(rx_size=self.buffer_size, tx_size=self.buffer_size)

        # Connect to the COM port
        self.connect_port()

        # print("UART_RX ThreadId:",self.currentThreadId())

    def list_ports(self):

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                s.__del__()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def change_port(self, port):
        self.port = port

    def reset(self):
        self.UART_buffer = bytearray()

        # self.close_port()

        # self.connect_port()

    # Connect port - used in initialization
    def connect_port(self):

        try:
            # Setup up baud rate and port
            self.serial_connection.port = self.port
            self.serial_connection.baudrate = self.baud_rate

            # Close all and then open the connection
            self.serial_connection.close()
            self.serial_connection.__del__()
            self.serial_connection.open()

            print('Successfully connected to %s'%self.serial_connection.port)
            # Start the QT thread
            self.start(priority = QThread.TimeCriticalPriority)

        except Exception as error:
            available_ports = self.list_ports()
            print('Error in connecting to port : %s' % error)
            print('If your error was the wrong port, try these ports:')
            print(available_ports)
            print('The program is still running but will do nothing until you change the port')

    # To emergency close the port (used for debug)

    def close_port(self):
        self.serial_connection.close()
        self.terminate()

    def run(self):
        while self.serial_connection.is_open:
            try:
                data = self.serial_connection.read_all()
                if len(data) > 10000:
                    print('WARNING: more than 10000 elements in UART buffer')
                self.UART_buffer.extend(data)

                i = self.UART_buffer.find(b'\n')
                if i >= 0:
                    line = self.UART_buffer[:i+1].decode('utf-8').rstrip(',')
                    self.UART_buffer = self.UART_buffer[i+1:]
                    # print(datetime.datetime.now(), len(self.UART_buffer), line)
                    self.serial_to_manager_carrier.emit(line)

            except Exception as e:
                del self.UART_buffer
                self.UART_buffer = bytearray()
                print(e)
