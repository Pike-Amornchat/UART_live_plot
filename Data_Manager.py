from Modules import *
from Raw_Processor import *
from Application_Processor import *
from GUI_Plotter import *
from Storage import *

class Data_Manager(QThread):

    manager_to_plotter_carrier = Signal(list)
    manager_to_raw_processor_carrier = Signal(list)
    covariance_carrier = Signal(list)

    def __init__(self, main_app = None, serial_connection=None, user_connection=None, raw_processor_connection=None,
                 application_processor_connection=None, plotter_connection=None, storage_connection=None):
        super(Data_Manager, self).__init__()
        self.main_app = main_app
        # Pass all Signal connection objects into data manager
        self.serial_connection = serial_connection
        self.user_connection = user_connection
        self.raw_processor_connection = Raw_Processor(data_manager=self)
        self.plotter_connection = Plotter(data_manager=self,raw_processor=self.raw_processor_connection)
        self.storage_connection = Storage(data_manager=self,raw_processor=self.raw_processor_connection)
        # self.application_processor_connection = Application_Processor(data_manager=self,
        #                                                               raw_processor=self.raw_processor_connection)

        # Connect to the UART and UserInput Signal carriers
        self.serial_connection.serial_to_manager_carrier.connect(self.receive_UART)
        self.user_connection.user_to_manager_carrier.connect(self.receive_user_input)

        # Initialize the data manager class with default settings
        self.data_manager_init()

        # print("Data_Manager ThreadId:",self.currentThreadId())


    def check_valid_calibration(self,R, cov_acc, cov_ang):
        try:
            if len(R) == len(R[0])  and len(R) == 6:
                if len(cov_acc) == len(cov_acc[0])  and len(cov_acc) == 3:
                    if len(cov_ang) == len(cov_ang[0]) and len(cov_ang) == 3:
                        if np.linalg.cond(cov_ang) < 1 / sys.float_info.epsilon or np.linalg.cond(cov_acc) < 1/ sys.float_info.epsilon:
                            return True
        except Exception:
            return False
        return False

    # Signal receive methods
    def receive_UART(self,input_buffer=''):
        # print(time.time())
        self.raw_UART_input.append(input_buffer)
        if len(self.raw_UART_input) > 0:
            self.start(priority = QThread.TimeCriticalPriority)

    def receive_user_input(self,input_buffer=''):
        self.user_input.append(input_buffer.split(' '))
        if len(self.user_input) > 0:
            self.start(priority = QThread.TimeCriticalPriority)

    # Set operations methods for plot and remove functions
    def combine_list(self,list1,list2):
        return list(set(list1) | set(list2))

    def delete_from(self,list1,list2):
        return list(set(list1)-set(list2))

    def list_and(self,arr):
        newlist = arr[0]
        for i in range(len(arr)):
            newlist = list(set(newlist) & arr[i])
        return newlist

    def data_manager_init(self):
        # Initialize the input buffers
        self.raw_UART_input = []
        self.user_input = []

        # Declared for use within loop
        self.line = ''
        self.identifier = ''
        self.plot_index_list = []
        self.raw = ''

        # For startup sequence - will not transmit data to calculate unless fully correct
        self.R = []
        self.cov_acc = []
        self.cov_ang = []

        # Flag for valid covariance matrices
        self.start_flag = 0
        self.transmitting = 0

    def full_reset(self):
        self.storage_connection.reset()
        # self.plotter_connection.reset()
        # self.application_processor_connection.reset()
        self.raw_processor_connection.reset()
        self.serial_connection.reset()
        self.data_manager_init()

    def run(self):
        command = ''
        option = ''
        choice = ''

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
                    self.storage_connection.start_storing()
                elif option == 'stop':
                    self.storage_connection.stop()

            elif command == 'connection':
                if option == 'setport':
                    self.serial_connection.close_port()
                    self.serial_connection.change_port(choice)
                    self.serial_connection.connect_port()
                elif option == 'closeport':
                    self.serial_connection.close_port()
                    print('Port %s closed'%self.serial_connection.port)

            elif command == 'plot':
                options = self.user_input[0][1:]
                try:
                    for i in range(len(options)):
                        options[i] = Config.categories[options[i]]
                    decoded_options = self.list_and(options)
                    self.plot_index_list = self.combine_list(self.plot_index_list,decoded_options)
                except Exception:
                    self.plot_index_list = []
                self.plot_index_list.sort()
                print(self.plot_index_list)

                self.manager_to_plotter_carrier.emit(self.plot_index_list)

            elif command == 'remove':
                options = self.user_input[0][1:]
                try:
                    for i in range(len(options)):
                        options[i] = Config.categories[options[i]]
                    decoded_options = self.list_and(options)
                    self.plot_index_list = self.delete_from(self.plot_index_list,decoded_options)
                except Exception:
                    self.plot_index_list = []
                self.plot_index_list.sort()
                print(self.plot_index_list)
                self.manager_to_plotter_carrier.emit(self.plot_index_list)

            # Reset the user input

            self.user_input = []

        while len(self.raw_UART_input) > 0:
            try:
                # The raw input coming in will be the first one in our stack
                self.raw = self.raw_UART_input[0]
                # print(self.raw)
                # We can then delete the first element, because we are done with it
                self.raw_UART_input = self.raw_UART_input[1:]

                self.line = np.copy(np.asarray(self.raw.split(',')))
                self.identifier = self.line[0][0]

                # Remove identifier
                self.line[0] = self.line[0][2:]

                # If incoming line is just text then print it
                if self.identifier == 'T':
                    print(self.raw, " my time:", time.time())

                else:

                    self.line = np.asarray(self.line, dtype=float)

                    # If the system detects an S for start, will reinitialize everything again.
                    if self.identifier == 'S':
                        self.full_reset()

                    # If the identifier is a R - for R - sensor noise covariance matrix
                    elif self.identifier == 'R':
                        self.R.append(self.line)

                    # We also have a physical noise estimator for the acceleration,
                    # where the user holds in rest position, to find Ak
                    elif self.identifier == 'A':
                        self.cov_acc.append(self.line)

                    # Lastly, for angular velocity:
                    elif self.identifier == 'W':
                        self.cov_ang.append(self.line)

                    # Set a flag to tell the code to send the covariance just once and begin sending
                    elif self.identifier == 'C':
                        self.start_flag += 1

                    # Gyro data (G)
                    elif self.identifier == 'G':

                        # This line only does this once - on the first G symbol. It detects whether or not
                        # the program can run.
                        if self.start_flag == 1:
                            if self.check_valid_calibration(self.R,self.cov_ang,self.cov_ang):
                                self.covariance_carrier.emit([self.R,self.cov_ang,self.cov_ang])
                                self.transmitting = 1
                            else:
                                print('Error in covariance matrix - system needs a soft reset from microcontroller')
                            self.start_flag = 2
                        elif self.start_flag == 0:
                            print('Error in covariance matrix - system needs a soft reset from microcontroller')
                            self.start_flag = 2
                        # If now ready to transmit:
                        if self.transmitting == 1:
                            self.manager_to_raw_processor_carrier.emit(self.line)
            except Exception as e:
                print(e)
                print('Incomplete line.')
