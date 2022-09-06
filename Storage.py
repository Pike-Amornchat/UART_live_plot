import wsgiref.validate

from Modules import *


class Storage(QThread):

    def __init__(self, data_manager=None, raw_processor=None):
        super(Storage, self).__init__()
        self.data_manager_connection = data_manager
        self.raw_processor_connection = raw_processor

        self.running = False

        self.raw_processor_connection.raw_processor_to_storage_carrier.connect(self.receive_raw)

    def receive_raw(self,input_buffer=''):
        if self.running:
            self.f.write('%s,'%datetime.datetime.now() + ','.join(input_buffer) + '\n')

    def start_storing(self):
        now = str(datetime.datetime.now()).replace(':', '_')
        self.f = open('%s.txt' % now, 'w')
        self.f.write('Text file for storing data')
        time.sleep(0.01)
        if os.path.isfile('%s.txt' % now):
            self.running = True
            print('A new text file has been created')
        return now

    def reset(self):
        self.stop()

    def stop(self):
        if self.running:
            self.running = False
            self.f.close()
            print('Stopped storing data - text file closed.')
