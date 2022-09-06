from Modules import *


class Plotter(QThread):

    def __init__(self, data_manager=None,raw_processor=None):
        super(Plotter, self).__init__()
        self.data_manager_connection =  data_manager
        self.raw_processor_connection = raw_processor

        self.plot_window = pg.GraphicsWindow(title='Dynamic Plotting with PyQtGraph')

        self.plotter_init()

        self.raw_processor_connection.raw_processor_to_plotter_carrier.connect(self.receive_and_update)
        self.data_manager_connection.manager_to_plotter_carrier.connect(self.plot_on_receive_data)

        self.plot_window.update()

        # print("Plotter ThreadId:",self.currentThreadId())

    def plot_on_receive_data(self,plot_index_list = []):
        self.plotter_init()

        self.plotting_index = plot_index_list
        curve_name = []
        pen = []
        for i, index in enumerate(plot_index_list):
            curve_name.append(Config.labels[str(index)])
            pen.append(Config.pen[i % len(Config.pen)])
        self.Add_new_plot(curve_number = len(plot_index_list),pen = pen, curve_name = curve_name )

    def receive_and_update(self,input_buffer=[]):

        counter = 0
        for i in self.plotting_index:
            self.y[i] = input_buffer[i].buffer
            self.x[i] = input_buffer[0].buffer
            self.curve_list[counter].setData(self.x[i], self.y[i])
            counter += 1
        
        self.plot_window.update()

    def plotter_init(self):
        try:
            for plot in self.plot_list:
                plot.clear()
            del self.curve_list
            del self.plot_list
        except:
            pass

        self.plot_window.clear()
        #data setup

        self.plotting_index = []

       
        self.plot_list = []
        self.curve_list = []
        # self.databufferHandler = []
        self.x = [Dynamic_RingBuff(Config.plot_size) for i in range(46)]
        self.y = [Dynamic_RingBuff(Config.plot_size) for i in range(46)]

        # self.start(priority = QThread.NormalPriority)

    def Add_new_plot(self, size = (600,350), pen = [(255,0,0), (255,0,0)], curve_number = 2, curve_name = ["sin1","sin2"]):
        self.plot = self.plot_window.addPlot()
        self.plot.resize(*size)
        self.plot.showGrid(x=True, y=True)
        self.plot.setLabel('left', 'amplitude', 'V')
        self.plot.setLabel('bottom', 'time', 's')
        self.plot.addLegend()
        self.plot_list.append(self.plot)
        
        for i in range(curve_number):
            self.Add_curve(plot = self.plot, pen = pen[i], Name = curve_name[i])


    def Add_curve(self,plot = None, pen = (255,0,0), Name = ""):
        self.curve = plot.plot(self.x[-1].buffer, self.y[-1].buffer, pen=pen, name = Name)
        self.curve_list.append(self.curve)

    def run(self):
        pass