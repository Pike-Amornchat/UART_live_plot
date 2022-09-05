from Modules import *


class Plotter(QThread):

    def __init__(self,data_manager=None,raw_processor=None):
        super(Plotter, self).__init__()
        self.data_manager_connection =  data_manager
        self.raw_processor_connection = raw_processor

        self.plotter_init()

        self.raw_processor_connection.raw_processor_to_plotter_carrier.connect(self.receive_raw)

    def receive_raw(self,input_buffer=''):
        for i in range(len(self.data_buffer)):
            self.data_buffer[i].add(input_buffer[i])

    def plotter_init(self):
        self.data_buffer = [Dynamic_RingBuff(Config.plot_size + 2) for i in range(46)]
        self.start(priority=QThread.NormalPriority)

    def run(self):
        # return
        while True:
            if len(self.data_buffer[0].buffer) > 0:
                pass
                # for i in range(len(self.data_buffer)):
                #     print(str(i) + ' ',self.data_buffer[i].buffer)
                # print('\n')