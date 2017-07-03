import wx
import SL
import datetime
from wx.lib.plot import PolyLine, PlotCanvas, PlotGraphics
import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure


class MyGraph(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          'Plotting File Data')

        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)
        self.canvas = PlotCanvas(panel)
        self.canvas.Draw(self.createPlotGraphics())

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)

        panel.SetSizer(sizer)

    # ----------------------------------------------------------------------
    def getData(self):
        data = SL.load_solar_light_file('BA170101.uvb')

        return data

    # ----------------------------------------------------------------------
    def createPlotGraphics(self):
        """"""
        data1 = self.getData()

        line1 = PolyLine(list(zip(data1.index.to_julian_date(), data1['SUV 2747'].values)), legend='Wide Line', colour='green', width=5)

        return PlotGraphics([line1], "25,000 Points", "Value X", "")

    def pydate2wxdate(self, date):
        assert isinstance(date, (datetime.datetime, datetime.date))
        tt = date.timetuple()
        dmy = (tt[2], tt[1] - 1, tt[0])
        return wx.DateTimeFromDMY(*dmy)


class DataLoggerWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "ComPlotter", (100, 100), (640, 480))

        self.SetBackgroundColour('#ece9d8')

        # Flag variables
        self.isLogging = False

        # Create plot area and axes
        self.fig = Figure(facecolor='#ece9d8')
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        self.canvas.SetPosition((0, 0))
        self.canvas.SetSize((640, 320))
        self.ax = self.fig.add_axes([0.08, 0.1, 0.86, 0.8])
        self.ax.autoscale(True)
        #self.ax.set_xlim(0, 1440)
        #self.ax.set_ylim(-100, 1100)
        self.data = self.getData()

        self.ax.plot(self.data.index.time, self.data['SUV 2747'].values)

        # Create text box for event logging
        self.log_text = wx.TextCtrl(
            self, -1, pos=(140, 320), size=(465, 100),
            style=wx.TE_MULTILINE)
        self.log_text.SetFont(
            wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))

        # Create timer toonStartStopButton read incoming data and scroll plot
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.GetSample, self.timer)

        # Create start/stop button
        self.start_stop_button = wx.Button(
            self, label="Start", pos=(25, 320), size=(100, 100))
        self.start_stop_button.SetFont(
            wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.start_stop_button.Bind(
            wx.EVT_BUTTON, self.onStartStopButton)

    def GetSample(self, event=None):
        # Get a line of text from the serial port
        sample_string = self.ser.readline()

        # Add the line to the log text box
        self.log_text.AppendText(sample_string)

        # If the line is the right length, parse it
        if len(sample_string) == 15:
            sample_string = sample_string[0:-1]
            sample_values = sample_string.split()

            for m in range(self.M):
                # get one value from sample
                value = int(sample_values[m])
                self.x[m][0:99] = self.x[m][1:]
                self.x[m][99] = value

            # Update plot
            self.ax.cla()
            self.ax.autoscale(False)
            self.ax.set_xlim(0, self.N - 1)
            self.ax.set_ylim(-100, 1100)
            for m in range(self.M):
                self.ax.plot(self.n, self.x[m])
            self.canvas.draw()

    def getData(self):
        data = SL.load_solar_light_file('BA170101.uvb')

        return data

    def onStartStopButton(self, event):
        return

if __name__ == '__main__':
    app = wx.PySimpleApp()
    window = DataLoggerWindow()

    window.Show()
    app.MainLoop()

#    app = wx.App(False)
#    frame = MyGraph()
#    frame.Show()
#    app.MainLoop()