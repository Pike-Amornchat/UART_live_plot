from Modules import *


class Plotter(QThread):

    def __init__(self,sampleinterval=0.01, timewindow=10., data_manager=None,raw_processor=None):
        super(Plotter, self).__init__()
        self.data_manager_connection =  data_manager
        self.raw_processor_connection = raw_processor

        self.sampleinterval = sampleinterval
        self.timewindow = timewindow

        
        self.win = pg.GraphicsWindow(title='Dynamic Plotting with PyQtGraph')

        self.plotter_init()

        self.raw_processor_connection.raw_processor_to_plotter_carrier.connect(self.receive_raw)
        self.data_manager_connection.manager_to_plotter_carrier.connect(self.who_to_plot)

        self.win.update()

        # print("Plotter ThreadId:",self.currentThreadId())

    def who_to_plot(self,plot_index_list = []):
        print("Got new plot",time.time())
        del self.curveHandler
        del self.pltHandler
        self.win.clear()
        self.plotter_init()
        cirve_name = []
        pen = []
        for index in plot_index_list:
            cirve_name.append(Config.labels[str(index)])
            pen.append(Config.pen[random.randint(0, len(Config.pen)-1)])
        self.Add_new_plot(curve_number = len(plot_index_list),timewindow=10,pen = pen, curve_name = cirve_name )

        print("Ok to plot",time.time())

    def receive_raw(self,input_buffer=''):
        for i in range(len(self.data_buffer)):
            self.data_buffer[i].add(input_buffer[i])

        print(self.data_buffer)

        for i in range(1,len(self.curveHandler)):
            self.databufferHandler[i].append( input_buffer[i]) #self.getdata()
            self.y[i][:] = self.databufferHandler[i]
        # self.x = self.databufferHandler[0]
        for i in range(1,len(self.curveHandler)):
            self.curveHandler[i].setData(self.x[i], self.y[i])
        
        self.win.update()

    def plotter_init(self):

        self.data_buffer = [Dynamic_RingBuff(Config.plot_size + 2) for i in range(46)]

         #data setup
        self.plot_num = 0
        self.pltHandler = []
        self.curveHandler = []
        self.databufferHandler = []
        self.x = []
        self.y = []

        self.feedInDataHandler = []
        # Data stuff
        self._interval = int(self.sampleinterval*1000)
        self._bufsize = int(self.timewindow/self.sampleinterval)

        # self.start(priority = QThread.NormalPriority)

    def Add_new_plot(self, size = (600,350), timewindow = 10, pen = [(255,0,0), (255,0,0)], curve_number = 2, curve_name = ["sin1","sin2"]):
        self.plt = self.win.addPlot()#pg.plot(title='Dynamic Plotting with PyQtGraph')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'amplitude', 'V')
        self.plt.setLabel('bottom', 'time', 's')
        self.plt.addLegend()
        self.pltHandler.append(self.plt)
        
        for i in range(curve_number):
            self.Add_curve(plt = self.plt,timewindow = timewindow, pen = pen[i], Name = curve_name[i])
        
        self.plot_num += 1

    def Add_curve(self,plt = None, timewindow = 10, pen = (255,0,0), Name = ""):
        self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.databufferHandler.append(self.databuffer)

        self.x.append( np.linspace(-timewindow, 0.0, self._bufsize) )
        self.y.append( np.zeros(self._bufsize, dtype=np.float) )

        self.curve = plt.plot(self.x[-1], self.y[-1], pen=pen, name = Name)
        self.curveHandler.append(self.curve)


    def run(self):
        # return
        while True:
            if len(self.data_buffer[0].buffer) > 0:
                for i in range(len(self.data_buffer)):
                    print(str(i) + ' ',self.data_buffer[i].buffer)
                print('\n')