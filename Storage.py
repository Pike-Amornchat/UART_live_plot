from Modules import *


class Storage(QThread):

    def __init__(self, data_manager=None, raw_processor=None):
        super(Storage, self).__init__()
        self.data_manager_connection = data_manager
        self.raw_processor_connection = raw_processor

        self.storage_init()

        self.raw_processor_connection.raw_processor_to_storage_carrier.connect(self.receive_raw)

        # print("Storage ThreadId:",self.currentThreadId())

    def receive_raw(self,input_buffer=''):
        for i in range(len(self.data_buffer)):
            self.data_buffer[i].add(input_buffer[i])

    def storage_init(self):
        self.data_buffer = [Dynamic_RingBuff(Config.plot_size + 2) for i in range(46)]
        self.start(priority = QThread.LowestPriority)

    def run(self):
        while True:
            pass
            # for i in range(len(self.data_buffer)):
            #     print(str(i) + ' ',self.data_buffer[i].buffer)
            # print('\n')