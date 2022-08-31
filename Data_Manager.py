from Modules import *


class Data_Manager(QThread):

    def __init__(self, serial_connection, ):
        super(Data_Manager, self).__init__()

        # Pass the UART connection object into data manager
        self.serial_connection = serial_connection
        self.raw_UART_input = []
        self.user_input = []

        # Declared for use within loop
        self.line = ''
        self.identifier = ''

        self.serial_connection.serial_to_manager_carrier.connect(self.receive_UART)
        self.user_input_thread.connect(self.receive_UART)

    def receive_UART(self,input_buffer=''):
        self.raw_UART_input.append(input_buffer)

    def receive_user_input(self,input_buffer=''):
        self.user_input.append(input_buffer)