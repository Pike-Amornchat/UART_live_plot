from Modules import *


class Plotter(QThread):

    """
    This thread is only called upon receiving new data, and creates a plot containing all of the data specified from
    the user. Refresh happens upon new data, update of which data happens upon user input receive.

    The window is referred to as 'window', and the actual axes and scales are referred to as 'plots'. Each individual
    line of data is called a 'curve'.
    """

    def __init__(self, data_manager=None,raw_processor=None):

        # QThreads inheritance
        super(Plotter, self).__init__()

        # Make an instance of data manager and raw processor in order to connect
        self.data_manager_connection =  data_manager
        self.raw_processor_connection = raw_processor

        # Make 1 plot window, ready to place a plot
        self.plot_window = pg.GraphicsWindow(title='Dynamic Plotting with PyQtGraph')

        # Initialize the plotter by making arrays/buffers for data
        self.plotter_init()

        # Connect to Signal from raw processor and data manager
        self.raw_processor_connection.raw_processor_to_plotter_carrier.connect(self.receive_and_update)
        self.data_manager_connection.manager_to_plotter_carrier.connect(self.plot_on_receive_command)

        # Update plot window after init to show empty axes
        self.plot_window.update()

    def plot_on_receive_command(self,plot_index_list = []):

        """
        Method connected by Signal from data manager, telling the plotter what to plot. Sets up curves array and pen,
        the updates the plot by calling update_plot method.
        :param plot_index_list: Default buffer for Signal - Expects list of int, specifying the indices to plot
        :return: None
        """

        # Call init to reset all buffers - this deletes the current plot so a new one has to be added by Update_plot()
        self.plotter_init()

        # Store current plotting index list and initialize new lists for the colour and labels
        self.plotting_index = plot_index_list
        curve_name = []
        pen = []

        # Go through each required data set and assign names and colours
        for i, index in enumerate(plot_index_list):
            curve_name.append(Config.labels[str(index)])
            pen.append(Config.pen[i % len(Config.pen)])

        # Update the plot, based on these new curves and its attributes
        self.Update_plot(curve_number = len(plot_index_list),pen = pen, curve_name = curve_name )

    def receive_and_update(self,input_buffer=[]):

        """
        Method for receiving raw plot data from Signal. Receives all of the data calculated, but only plots what is
        instructed by the user. Updates the data buffers in each defined plot, then updates the window to reflect
        the changes.
        :param input_buffer: Default buffer for Signal - Expects list[46] of float
        :return: None
        """

        # Same thing as for i, index in enumerate, but just with a counter.
        counter = 0

        # For every user-specified index, update only the required fields, then set the data in curves array
        for i in self.plotting_index:
            self.y[i] = input_buffer[i].buffer
            self.x[i] = input_buffer[0].buffer
            self.curve_list[counter].setData(self.x[i], self.y[i])
            counter += 1

        # Update plot based on the set data
        self.plot_window.update()

    def plotter_init(self):

        """
        Initialization method for the class - clears all data buffers if they still exist and clears plot window.
        :return: None
        """

        # For all remaining plots, clear the plot (there is only 1 plot).
        try:
            for plot in self.plot_list:
                plot.clear()
            # Delete any instance of curves and plot list if they still exist
            del self.curve_list
            del self.plot_list
        except:
            pass

        # Clear the plot window
        self.plot_window.clear()

        # Re-initialize the indices to plot
        self.plotting_index = []

        # Re-initialize the list of plots (1 plot) and list of curves - they are both objects
        self.plot_list = []
        self.curve_list = []

        # Initialize the x and y storage lists
        self.x = [Dynamic_RingBuff(Config.plot_size) for i in range(46)]
        self.y = [Dynamic_RingBuff(Config.plot_size) for i in range(46)]

    def reset(self):

        """
        Reset method called by Data Manager - resets all buffers using init()
        :return: None
        """
        self.plotter_init()

    def Update_plot(self, size = (600,350), pen = None, curve_number = 2, curve_name = None):

        """
        Updates the plot, when given new curves - DOES NOT UPDATE THE DATA; only updates the plot with new legend, axes,
        etc. Also assigns pen colour and label, but does nothing beyond that.
        :param size: Tuple[2] of int - pixel size of opening plot
        :param pen: List of tuple(3) containing RGB of each plot's designated colour
        :param curve_number: Int - specifies how many curves to draw
        :param curve_name: List of str - labels for each plot
        :return: None
        """

        # Add a plot to the window
        self.plot = self.plot_window.addPlot()

        # Set the size of the window to the inputted size
        self.plot.resize(*size)

        # Show the grid lines in x and y
        self.plot.showGrid(x=True, y=True)

        # Set the label of the y and x axes
        self.plot.setLabel('left', 'Value', '[SI Units]')
        self.plot.setLabel('bottom', 'time', 's')

        # Add the legend, and then add this plot to the list of running plots
        self.plot.addLegend()
        self.plot_list.append(self.plot)

        # Add each curve's characteristics into the plot
        for i in range(curve_number):
            self.Add_curve(plot = self.plot, pen = pen[i], Name = curve_name[i])

    def Add_curve(self,plot = None, pen = (255,0,0), Name = ""):

        """
        Adds each curve's attributes into the plot (this does not actually plot the data)
        :param plot: The plot object (we only have 1 plot object)
        :param pen: Tuple[3] containing RGB of each plot's designated colour
        :param Name: List of str - labels for each plot
        :return: None
        """

        # Make a plot object (Remember, not the line) and adds some temporary data to it - will updated away
        self.curve = plot.plot(self.x[-1].buffer, self.y[-1].buffer, pen=pen, name = Name)

        # Add this curve to the lists of all curves
        self.curve_list.append(self.curve)

    # Kept for future implementation
    def run(self):
        pass