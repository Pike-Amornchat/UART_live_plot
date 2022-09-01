from Modules import *


class Raw_Processor(QThread):

    def __init__(self,data_manager=None):
        super(Raw_Processor, self).__init__()
        self.data_manager = data_manager
        self.init_raw_processor()

    def init_raw_processor(self):
        self.R = []
        self.cov_acc = []
        self.cov_ang = []
        self.cov_buffer = []

        self.

    def receive_data(self,input_buffer=''):
        self.cov_buffer.append(input_buffer)

    def receive_covariance(self,input_buffer=''):
        self.cov_buffer.append(input_buffer)