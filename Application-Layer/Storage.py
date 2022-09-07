from Modules import *


class Storage(QThread):

    """
    This class controls storing data. Upon receiving the instruction from Data Manager,
    a flag for storing data is triggered and storing data starts. The text file is named after the date and time of
    the store start method.
    """

    def __init__(self, raw_processor=None):

        # QThreads inheritance
        super(Storage, self).__init__()

        # Form instances of the data manager and raw processor class in order to connect through Signal
        self.raw_processor_connection = raw_processor

        # Initialize no storage until asked
        self.running = False

        # Connect to raw processor using Signal
        self.raw_processor_connection.raw_processor_to_storage_carrier.connect(self.receive_raw)

    def receive_raw(self,input_buffer=''):

        """
        Method connected to Data Manager by Signal to receive raw data - writes data into text file on receive
        :param input_buffer: Default buffer for Signal - Expects list of str (data but in string format)
        :return: None
        """

        # If flag is triggered:
        if self.running:

            # Write to the opened text file using specified format
            self.f.write('%s,'%datetime.datetime.now() + ','.join(input_buffer) + '\n')

    def start_storing(self):

        """
        Initializes the new text file using the current date and time.
        :return: String containing date and time
        """

        # Get the current date and time
        now = str(datetime.datetime.now()).replace(':', '_')

        # Open a new text file with this name
        self.f = open('%s.txt' % now, 'w')

        # Write the title in
        self.f.write('Text file for storing Gyroscope data\n')

        # Sleep just to be sure the file is properly in there
        time.sleep(0.01)

        # If the file now exists
        if os.path.isfile('%s.txt' % now):

            # Trigger the running flag
            self.running = True
            print('A new text file has been created')

        # Return the new date and time
        return now

    def reset(self):

        """
        Reset method called by Data Manager - stops recording data.
        :return:
        """

        self.stop()

    def stop(self):

        """
        Stop storing method - untriggers the flag and closes the text file
        :return: NOne
        """

        # Check if the flag is active
        if self.running:

            # If yes, turn it off
            self.running = False

            # Close the text file and output to user
            self.f.close()
            print('Stopped storing data - text file closed.')
