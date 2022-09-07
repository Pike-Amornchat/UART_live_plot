from Modules import *
from Raw_Processor import *
from Application_Processor import *
from GUI_Plotter import *
from Storage import *

class Data_Manager(QThread):

    """
    This is the most important thread in the program - it takes the data in from PySerial and decides where to send it/
    acts upon the instructions - this is done through a simple identifier protocol, a letter at the start of a line.
    Note that this thread DOES NOT RUN ALL THE TIME - due to optimization, it runs upon data reception.

    Also, it controls, interprets and issues commands issued by the command line from the user.

    T = text
    S = start
    R = covariance estimate of sensor noise
    A = covariance estimate of acceleration enviromnment noise
    W = covariance estimate of angular velocity environment noise
    C = complete
    G = gyro data (just data)

    From here, the manager acts upon it, printing text, calling resets with start and verifying the covariance matrices
    before emitting.

    As for the user input, it uses set notation and a dictionary in order to decide what the user wants plotted/removed.
    The user may also choose to connect to a different port, or start recording data in a text file.



    The commands are as follows: [terminate,store,connection,plot,remove]:

    terminate (terminates the program completely)

    store start (creates a new text file and starts storing data in it)
    store stop (stops storing data in that file - the file will not appear in PyCharm until the program is stopped)

    connection closeport (close and terminate that port)
    connection setport _____[e.g. COM9 defalt] (changes ports to whatever the user wants)

    plot ____[raw,filter,smooth,x,y,z,norm,vel,acc,ang,jerk,temp,all] - any combination will yield results, e.g. :

    plot smooth norm acc (order doesn't matter) will yield a plot of the smoothed norm of the acceleration.

    plot adds curves to the existing plot, e.g. :

    plot raw
    plot acc

    plots all raw data and all acceleration data

    remove ____[raw,filter,smooth,x,y,z,norm,vel,acc,ang,jerk,temp,all] - same as plot, but removes what you put in.
    """

    # Create a signal class to connect to the plotter (feed user input), and raw processor to feed covariance
    # and raw data.
    manager_to_plotter_carrier = Signal(list)
    manager_to_raw_processor_carrier = Signal(list)
    covariance_carrier = Signal(list)

    def __init__(self, serial_connection=None, user_connection=None):

        # QT inherit all of QThread
        super(Data_Manager, self).__init__()

        # Pass all Signal connection objects into data manager
        self.serial_connection = serial_connection
        self.user_connection = user_connection

        # The rest of them require data manager in order to do .connect() when receiving data, so self is passed in
        self.raw_processor_connection = Raw_Processor(data_manager=self)
        self.plotter_connection = Plotter(data_manager=self,raw_processor=self.raw_processor_connection)
        self.storage_connection = Storage(raw_processor=self.raw_processor_connection)
        self.application_processor_connection = Application_Processor(data_manager=self,
                                                                      raw_processor=self.raw_processor_connection)

        # Connect to the UART and UserInput Signal carriers
        self.serial_connection.serial_to_manager_carrier.connect(self.receive_UART)
        self.user_connection.user_to_manager_carrier.connect(self.receive_user_input)

        # Initialize the data manager class with default settings
        self.data_manager_init()

    def check_valid_calibration(self,R, cov_acc, cov_ang):

        """
        Checks for valid covariance matrices using matrix shape and invertibility,
        will be singular if left too still during environment noise calibration.
        DOES NOT CHECK FOR NEGATIVE SEMIDEFINITENESS.
        :param R: 6x6 2D Numpy array - sensor noise covariance matrix
        :param cov_acc: - 3x3 2D Numpy array - physical/environment noise acceleration covariance matrix
        :param cov_ang: - 3x3 2D Numpy array - physical/environment noise angular velocity covariance matrix
        :return: Boolean - True if valid matrices, False if not.
        """
        try:
            if len(R) == len(R[0])  and len(R) == 6:
                if len(cov_acc) == len(cov_acc[0])  and len(cov_acc) == 3:
                    if len(cov_ang) == len(cov_ang[0]) and len(cov_ang) == 3:
                        if np.linalg.cond(cov_ang) < 1 / sys.float_info.epsilon or np.linalg.cond(cov_acc) < 1/ sys.float_info.epsilon:
                            return True
        except Exception:
            return False
        return False

    def receive_UART(self,input_buffer=''):

        """
        Signal receive method for UART MCU data - expects string
        :param input_buffer: Default buffer for Signal connect
        :return: None
        """

        # If receive emit from Signal, then append it into the buffer
        self.raw_UART_input.append(input_buffer)

        # ///////SUPER IMPORTANT/////// - This is the most critical optimization - it starts the thread ONCE
        # (because there is no while loop in run) whenever data arrives - the thread must be open and closed like this
        # in order to make it not lag by 50,000% (for real).
        if len(self.raw_UART_input) > 0:
            self.start(priority = QThread.TimeCriticalPriority)

    def receive_user_input(self,input_buffer=''):

        """
        Signal receive method for UserInput thread - expects string
        :param input_buffer: Default buffer for Signal connect
        :return: None
        """

        # If receive emit from Signal, then append it into the buffer
        self.user_input.append(input_buffer.split(' '))

        # ///////SUPER IMPORTANT/////// - This is the most critical optimization - it starts the thread ONCE
        # (because there is no while loop in run) whenever data arrives - the thread must be open and closed like this
        # in order to make it not lag by 50,000% (for real).
        if len(self.user_input) > 0:
            self.start(priority = QThread.TimeCriticalPriority)

    # Set operations methods for plot and remove functions - set operations to determine user plot input

    def combine_list(self,list1,list2):

        """
        Logical OR for 2 lists
        :param list1: list of int
        :param list2: list of int
        :return: list of int containing the OR of the 2 lists
        """

        return list(set(list1) | set(list2))

    def delete_from(self,list1,list2):

        """
        Logical subtract for 2 lists
        :param list1: list of int - main list
        :param list2: list of int - list to subtract
        :return: list of int containing difference in 2 lists. If list1 is a proper subset of list2,
        then returns empty set.
        """
        return list(set(list1)-set(list2))

    def list_and(self,arr):

        """
        Logical AND for 2 lists
        :param arr: list of list of int (2D list)
        :return: list of int - the logical AND operation
        """

        newlist = arr[0]
        for i in range(len(arr)):
            newlist = list(set(newlist) & arr[i])
        return newlist

    def data_manager_init(self):

        """
        Init for data manager - variables done outside def __init__(self) for ease of reset.
        :return: None
        """

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

        """
        Upon seeing an S, data manager will reset every class using this method.
        Calling this calls reset from every class.
        :return: None
        """

        self.storage_connection.reset()
        self.plotter_connection.reset()
        self.application_processor_connection.reset()
        self.raw_processor_connection.reset()
        self.serial_connection.reset()
        self.data_manager_init()

    def run(self):

        """
        Run is called upon receiving data and only runs once, checking the identifier and issuing the commands inputted
        by the user as well as managing the data in from UART.
        :return: None
        """

        command = ''
        option = ''
        choice = ''

        # Check why run was called - user input or data?
        if len(self.user_input) > 0:

            # Basic syntax check and relabelling
            try:

                # Read the first command
                command = self.user_input[0][0]

                # If they want to termiante then end the program here.
                if command == 'terminate':
                    print('Terminating program.')
                    sys.exit()

                # If not, then determine the command and choice.
                option = self.user_input[0][1]
                if command == 'connection' and option == 'setport':
                    choice = self.user_input[0][2]

            except Exception:
                print('Sorry, incorrect syntax. Please try again.')

            # Check for store - data manager tells storage class to start/stop storing.
            if command == 'store':
                if option == 'start':
                    self.storage_connection.start_storing()
                elif option == 'stop':
                    self.storage_connection.stop()
                else:
                    print('Sorry, incorrect syntax. Please try again.')

            # Check for connection
            elif command == 'connection':

                # If setport valid, then close current port, change port and try connect again.
                if option == 'setport':
                    self.serial_connection.close_port()
                    self.serial_connection.change_port(choice)
                    self.serial_connection.connect_port()

                # If closeport, then close the port
                elif option == 'closeport':
                    self.serial_connection.close_port()
                    print('Port %s closed'%self.serial_connection.port)
                else:
                    print('Sorry, incorrect syntax. Please try again.')

            # Check for plot
            elif command == 'plot':

                # Options is now everything after 'plot'
                options = self.user_input[0][1:]

                # For every option, go and search if the option is in the Config dictionary or not
                try:

                    # If found, replace each one with arrays of indices
                    for i in range(len(options)):
                        options[i] = Config.categories[options[i]]

                    # Perform AND on all of the arrays to remove overlap
                    decoded_options = self.list_and(options)

                    # Combine with current ones to add to plot
                    self.plot_index_list = self.combine_list(self.plot_index_list,decoded_options)

                # If not found, then reset the plot list to nothing
                except Exception:
                    print('Sorry, category not found. Keeping current plot.')

                # Sort it at the end to look nicer
                self.plot_index_list.sort()

                # Display the choice
                print('Indices ready to plot : ',self.plot_index_list)

                # Emit the chosen port to the plotter
                self.manager_to_plotter_carrier.emit(self.plot_index_list)

            # Same logic as plot, but with remove:
            elif command == 'remove':

                # Options is now everything after 'remove'
                options = self.user_input[0][1:]

                # For every option, go and search if the option is in the Config dictionary or not
                try:

                    # If found, replace each one with arrays of indices
                    for i in range(len(options)):
                        options[i] = Config.categories[options[i]]

                    # Perform AND on all of the arrays to remove overlap
                    decoded_options = self.list_and(options)

                    # Subtract from current list
                    self.plot_index_list = self.delete_from(self.plot_index_list, decoded_options)

                # If not found, then reset the plot list to nothing
                except Exception:
                    print('Sorry, category not found. Keeping current plot.')

                # Sort it at the end to look nicer
                self.plot_index_list.sort()

                # Display the choice
                print('Indices ready to plot : ', self.plot_index_list)

                # Emit the chosen port to the plotter
                self.manager_to_plotter_carrier.emit(self.plot_index_list)

            else:
                print('Sorry, incorrect syntax. Please try again.')

            # Reset the user input at the end to clear the buffer

            self.user_input = []

        # If data is coming in:
        while len(self.raw_UART_input) > 0:
            try:

                # The raw input coming in will be the first one in our stack
                self.raw = self.raw_UART_input[0]

                # We can then delete the first element, because we are done with it
                self.raw_UART_input = self.raw_UART_input[1:]

                # Split into list, and extract the identifier
                self.line = np.copy(np.asarray(self.raw.split(',')))
                self.identifier = self.line[0][0]

                # Remove identifier from the rest of the data
                self.line[0] = self.line[0][2:]

                # If incoming line is just text then print it
                if self.identifier == 'T':
                    print(self.raw, " my time:", time.time())

                else:

                    # Change datatype to float
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

                            # Check if the calibration is valid
                            if self.check_valid_calibration(self.R,self.cov_ang,self.cov_ang):

                                # If yes, set the transmitting flag and emit the covariance matrices
                                self.covariance_carrier.emit([self.R,self.cov_ang,self.cov_ang])
                                self.transmitting = 1

                            # If not, tell user to soft reset
                            else:
                                print('Error in covariance matrix - system needs a soft reset from microcontroller')

                            # Set start_flag to 2 to only enter this loop once unless reset is called
                            self.start_flag = 2

                        # If system misses the start, then tell user to reset, and set the start flag to 2
                        elif self.start_flag == 0:
                            print('Error in covariance matrix - system needs a soft reset from microcontroller')
                            self.start_flag = 2

                        # If now ready to transmit, then emit the line
                        if self.transmitting == 1:
                            self.manager_to_raw_processor_carrier.emit(self.line)

            # This catches any incomplete lines sent over by PySerial if it does happen for whatever reason
            except Exception as e:
                print(e)
                print('Incomplete line.')
