from Modules import *


class Raw_Processor(QThread):

    def __init__(self,data_manager=None):
        super(Raw_Processor, self).__init__()

        self.data_manager = data_manager

        self.data_manager.covariance_carrier.connect(self.receive_covariance)
        self.data_manager.manager_to_raw_processor_carrier.connect(self.receive_data)

        self.init_raw_processor()

    def init_raw_processor(self):
        self.R = []
        self.cov_acc = []
        self.cov_ang = []
        self.cov_buffer = []
        self.data_buffer = []

        self.start()

    def receive_data(self,input_buffer=''):
        self.data_buffer.append(input_buffer)
        print('twice???')
        print(self.data_buffer)

    def receive_covariance(self,input_buffer=''):
        self.cov_buffer.append(input_buffer)
        self.R = self.cov_buffer[0][0]
        self.cov_acc = self.cov_buffer[0][1]
        self.cov_ang = self.cov_buffer[0][2]

    def run(self):
        while True:
            if len(self.data_buffer) != 0:
                #print('raw ',self.data_buffer)
                pass