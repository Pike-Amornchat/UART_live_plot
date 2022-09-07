from Modules import *


class Application_Processor(QThread):

    """
    This class controls all further data processing/application using the cleaned up data - can be used for
    Machine Learning, or simple threshold/cross-zero detection.
    """

    def __init__(self, data_manager=None, raw_processor=None):

        # Inherit QThreads
        super(Application_Processor, self).__init__()

        # Initialise the classes passed in
        self.data_manager_connection = data_manager
        self.raw_processor_connection = raw_processor

        # Initialize the buffers
        self.application_init()

        # Connect to Raw_Processor to receive clean data
        self.raw_processor_connection.raw_processor_to_application_carrier.connect(self.receive_raw)

    def receive_raw(self,input_buffer=''):

        """
        Method for receiving data connected by Signal - puts received data into a dynamic ring buffer.
        :param input_buffer: Default buffer for Signal - Expects list of float containing 1 time step of processed data
        :return: None
        """

        for i in range(len(self.data_buffer)):
            self.data_buffer[i].add(input_buffer[i])

    # Initializing method - used for reset
    def application_init(self):

        """
        Initializes data buffer - can be called to reset
        :return: None
        """

        self.data_buffer = [Dynamic_RingBuff(Config.plot_size) for i in range(46)]

    def reset(self):

        """
        Reset just clears the buffers - called by Data Manager
        :return: None
        """

        self.application_init()

    # Empty, but can be called every time data is sent from receive_raw()
    def run(self):
        pass