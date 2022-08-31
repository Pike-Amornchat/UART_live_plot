from Modules import *


class Data_Manager(QThread):

    manager_to_plotter_carrier = Signal(str)

    def __init__(self, serial_connection=None, user_connection=None):
        super(Data_Manager, self).__init__()

        # Pass the UART connection object into data manager
        self.serial_connection = serial_connection
        self.user_connection = user_connection
        self.raw_UART_input = []
        self.user_input = []

        # Declared for use within loop
        self.line = ''
        self.identifier = ''
        self.plot_index_list = []
        self.raw = ''

        self.serial_connection.serial_to_manager_carrier.connect(self.receive_UART)
        self.user_connection.user_to_manager_carrier.connect(self.receive_user_input)

        self.start()

    def receive_UART(self,input_buffer=''):
        self.raw_UART_input.append(input_buffer)

    def receive_user_input(self,input_buffer=''):
        self.user_input.append(input_buffer.split(' '))

    def combine_list(self,list1,list2):
        return list(set(list1) | set(list2))

    def delete_from(self,list1,list2):
        return list(set(list1)-set(list2))

    def list_and(self,arr):
        newlist = arr[0]
        for i in range(len(arr)):
            newlist = list(set(newlist) & arr[i])
        return newlist

    def full_reset(self):
        ''

    def run(self):
        while True:

            # Optimize the CPU - if nothing in then don't kill the CPU

            if len(self.raw_UART_input) == 0:
                time.sleep(0.0001)
            if len(self.user_input) == 0:
                time.sleep(0.0001)

            command = ''
            option = ''
            choice = ''
            while len(self.raw_UART_input) > 0 or len(self.user_input) > 0:

                if len(self.user_input) > 0:
                    try:
                        command = self.user_input[0][0]
                        option = self.user_input[0][1]
                        if command == 'connection' and option == 'setport':
                            choice = self.user_input[0][2]
                    except Exception:
                        print('Sorry, incorrect syntax. Please try again.')

                    if command == 'store':
                        if option == 'start':
                            print('Start storing data')
                        elif option == 'stop':
                            print('Stop storing data')

                    elif command == 'connection':
                        if option == 'setport':
                            self.serial_connection.close_port()
                            self.serial_connection.change_port(choice)
                            self.serial_connection.connect_port()
                        elif option == 'closeport':
                            self.serial_connection.close_port()

                    elif command == 'plot':
                        options = self.user_input[0][1:]

                        for i in range(len(options)):
                            options[i] = Config.categories[options[i]]

                        decoded_options = self.list_and(options)
                        self.plot_index_list = self.combine_list(self.plot_index_list,decoded_options)
                        print(self.plot_index_list)
                        self.manager_to_plotter_carrier.emit(self.plot_index_list)
                    self.user_input = []

                elif len(self.raw_UART_input) > 0:

                    # The raw input coming in will be the first one in our stack
                    self.raw = self.raw_UART_input[0]

                    # We can then delete the first element, because we are done with it
                    del self.raw_UART_input[0]

                    self.line = np.copy(np.asarray(self.raw.split(',')))
                    self.identifier = self.line[0][0]
                    self.line[0] = self.line[0][2:]

                    # If incoming line is just text then print it
                    if self.identifier == 'T':
                        print(self.raw)

                    # If the system detects an S for start, will reinitialize everything again.
                    elif self.identifier == 'S':
                        print(self.raw)

                    # If the identifier is a R - for R - sensor noise covariance matrix
                    elif self.identifier == 'R':
                        print(self.raw)

                    # We also have a physical noise estimator for the acceleration,
                    # where the user holds in rest position, to find Ak
                    elif self.identifier == 'A':
                        print(self.raw)

                    # Lastly, for angular velocity:
                    elif self.identifier == 'w':
                        print(self.raw)

                    # If the system detects a C for complete, the calibration is done.
                    elif self.identifier == 'C':
                        print(self.raw)

                    # Gyro data (G)
                    elif self.identifier == 'G':
                        ''