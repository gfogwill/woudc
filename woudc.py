import SL
import os
import wx
import matplotlib
import pandas as pd
from string import Template
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure

matplotlib.use('WXAgg')


class Window(wx.Frame):
    def __init__(self):
        """ Creo la ventana con los botones y todo. """
        wx.Frame.__init__(self, None, -1, "Servicio Meteorologico Nacional - VAyGeo", (100, 100), (940, 580))
        self.SetBackgroundColour('#ece9d8')
        self.ReadStationData()

        # Variables
        self.DirPath = 'C:\\'
        self.OutPath = 'C:\\'
        self.cal_factor = 1
        self.FileList = []
        self.converted_file_list = []

        # Create plot area and axes
        self.fig = Figure(facecolor='#ece9d8')
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        self.canvas.SetPosition((0, 0))
        self.canvas.SetSize((640, 320))
        self.ax = self.fig.add_axes([0.08, 0.1, 0.86, 0.8])
        self.ax.autoscale(True)

        self.SL_data = SL.SL()

        # Create text box for event logging
        self.dataPath_text = wx.TextCtrl(self, -1, pos=(140, 320), size=(465, 25))
        self.outPath_text = wx.TextCtrl(self, -1, pos=(140, 360), size=(465, 25))

        # Texto para tomar el factor de calibración.
        wx.StaticText(self, -1, "Factor de calibración:", pos=(200, 400))
        self.t_cal_factor = wx.TextCtrl(self, -1, '1', pos=(320, 400), size=(50, 25))
        self.t_cal_factor.Bind(wx.EVT_KEY_UP, self.onCalFactorEdit)

        # Cuadro para listar archivos.
        self.t2 = wx.ListBox(self, -1, pos=(640, 32), size=(200, 300), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.t2.Bind(wx.EVT_LISTBOX_DCLICK, self.plotFile, self.t2)

        # Boton de directorio de datos:
        self.datadir_button = wx.Button(self, label='Datos', pos=(25, 320), size=(100, 25))
        self.datadir_button.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.datadir_button.Bind(wx.EVT_BUTTON, self.onDatadirButton)

        # Boton de directorio de salida de datos:
        self.outdir_button = wx.Button(self, label='Convertidos', pos=(25, 360), size=(100, 25))
        self.outdir_button.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.outdir_button.Bind(wx.EVT_BUTTON, self.onOutdirButton)

        # Create start/stop button
        self.convert_button = wx.Button(self, label='Convertir', pos=(25, 400), size=(100, 25))
        self.convert_button.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.convert_button.Bind(wx.EVT_BUTTON, self.onConvertButton)

        # Create start/stop button
        self.edit_button = wx.Button(self, label='Editar', pos=(25, 440), size=(100, 25))
        self.edit_button.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.edit_button.Bind(wx.EVT_BUTTON, self.onEditButton)

        # Texto para tomar el factor de calibración.
        estaciones = self.stations_data.Estacion.values
        wx.StaticText(self, -1, "Estación:", pos=(380, 400))
        self.combo_est = wx.ComboBox(self, -1, '1', pos=(440, 400), size=(50, 25), choices=estaciones)
        self.combo_est.Bind(wx.EVT_TEXT, self.SetStationParameters)

        wx.StaticText(self, -1, "N° de sensor:", pos=(640, 360))
        wx.StaticText(self, -1, "N° de estación:", pos=(640, 390))
        wx.StaticText(self, -1, "GAW ID:", pos=(640, 420))
        wx.StaticText(self, -1, "Latitud:", pos=(640, 450))
        wx.StaticText(self, -1, "Longitud:", pos=(640, 480))
        wx.StaticText(self, -1, "Altura:", pos=(640, 510))

        self.t_sens_numb = wx.TextCtrl(self, -1, '-', pos=(740, 355), size=(70, 25))
        self.t_station_numb = wx.TextCtrl(self, -1, '-', pos=(740, 385), size=(70, 25))
        self.t_gawid = wx.TextCtrl(self, -1, '-', pos=(740, 415), size=(70, 25))
        self.t_lat = wx.TextCtrl(self, -1, '-', pos=(740, 445), size=(70, 25))
        self.t_long = wx.TextCtrl(self, -1, '-', pos=(740, 475), size=(70, 25))
        self.t_alt = wx.TextCtrl(self, -1, '-', pos=(740, 505), size=(70, 25))

    def onCalFactorEdit(self, event):
        self.cal_factor = float(self.t_cal_factor.GetValue())

    def ReadStationData(self):
        self.stations_data = pd.read_csv('Estaciones.txt')

    def SetStationParameters(self, event):
        with open('Estaciones.txt') as stations_file:
            for line in stations_file:
                if line.startswith(self.combo_est.GetValue()):
                    station_data = line[:-1].split(',')

        self.t_sens_numb.SetValue(station_data[1])
        self.t_station_numb.SetValue(station_data[2])
        self.t_gawid.SetValue(station_data[3])
        self.t_lat.SetValue(station_data[4])
        self.t_long.SetValue(station_data[5])
        self.t_alt.SetValue(station_data[6])
        self.cal_factor = station_data[7]
        self.t_cal_factor.SetValue(station_data[7])

    def plotFile(self, event):

        self.SL_data, self.SL_date = SL.SL.load_solar_light_file(self.DirPath + '\\' + self.FileList[self.t2.GetSelection()])
        self.ax.clear()

        self.SL_data['Sensor1'] = self.SL_data['Sensor1'].values * 40 * 0.35 * float(self.cal_factor)

        self.SL_data = self.SL_data.tz_localize('UTC').tz_convert('America/Buenos_Aires')

        position_text = self.SL_data.index.date[-1].strftime('%Y-%m-%d') + ' 01:00'

        # Hago el grafico, cambio los limites, ajusto los ejes y pongo los titulos.
        self.ax.plot_date(self.SL_data.index.time, self.SL_data['Sensor1'].values, markersize=0.5, color='#00008D')
        self.ax.set_ylim(ymin=0, ymax=14)

        self.ax.set_yticks([0, 3, 6, 8, 11, 14], minor=False)
        self.ax.set_yticks([1, 2, 4, 5, 7, 9, 10, 12, 13], minor=True)
        self.ax.tick_params(axis='y', which='major', length=10, width=1.5)
        self.ax.tick_params(axis='y', which='minor', length=5, width=1)
        self.ax.grid(axis='y', b=None)
        self.ax.grid(axis='x')

        # Agrego los textos.
        self.ax.text(position_text, 1.5, 'Leve', verticalalignment='center')
        self.ax.text(position_text, 4.5, 'Moderado', verticalalignment='center')
        self.ax.text(position_text, 7, 'Alto', verticalalignment='center')
        self.ax.text(position_text, 9.5, 'Muy Alto', verticalalignment='center')
        self.ax.text(position_text, 12.5, 'Extremo', verticalalignment='center')

        # Pongo los colores del fondo
        self.ax.axhspan(0, 3, color='#329500')  # Low
        self.ax.axhspan(3, 6, color='#F7E400')  # Moderated
        self.ax.axhspan(6, 8, color='#F85900')  # High
        self.ax.axhspan(8, 11, color='#D8001D')  # Very High
        self.ax.axhspan(11, 14, color='#6B49c8')  # Extreme

        self.fig.canvas.draw()

    def GetFilesList(self):
        """ Hago una lista con todos los archivos del Solar Light
        que hay en el directorio seleccionado. """
        self.FileList = []
        self.converted_file_list = []

        for file in os.listdir(self.DirPath):
            if file.endswith('uvb'):
                self.FileList.append(file)

        return

    def getData(self):
        """ Abro un archivo de Solar Light """
        self.SL_data, self.SL_date = SL.load_solar_light_file('BA170101.uvb')

        return

    def onEditButton(self, event):
        os.startfile(self.DirPath + '\\' + self.FileList[self.t2.GetSelection()])
        if not self.t2.GetStringSelection().endswith(' (Editado)'):
            self.t2.SetString(self.t2.GetSelection(), self.t2.GetStringSelection() + ' (Editado)')

        return

    def onConvertButton(self, event):
        """Convierto los datos al formato de WOUDC con una plantilla que es foo.txt"""
        fi = open('foo.txt')
        fo_name = self.SL_date.strftime('%Y%m%d') + \
                  '.UV-Biometer.501.' + \
                  str(self.t_sens_numb.GetValue()) +\
                  '.smna.csv'

        fo = open(self.OutPath + '\\' + fo_name, 'w')

        src = Template(fi.read())
        fi.close()

        d = {'sensor_number': self.t_sens_numb.GetValue(),
             'numero_estacion': self.t_station_numb.GetValue(),
             'nombre_estacion': self.combo_est.GetValue(),
             'gaw_id': self.t_gawid.GetValue(),
             'lat': self.t_lat.GetValue(),
             'long': self.t_long.GetValue(),
             'altura': self.t_alt.GetValue(),
             'date': self.SL_date.strftime('%Y-%m-%d')}

        result = src.substitute(d)

        fo.write(result)
        self.SL_data.Sensor1 = self.SL_data.Sensor1 * float(self.cal_factor)
        self.SL_data[['Sensor1']].to_csv(fo, na_rep='', date_format='%H:%M:%S', float_format='%.7f', header=None)

        if not self.t2.GetStringSelection().startswith('* '):
            self.t2.SetString(self.t2.GetSelection(), '* ' + self.t2.GetStringSelection())

        self.t2.SetSelection(self.t2.GetSelection()+1)
        self.plotFile(wx.EVT_LEFT_DOWN)

        fo.close()

    def onDatadirButton(self, event):
        """ Selecciono la carpeta donde estan los archivos a procesar """
        dialog = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.DirPath = dialog.GetPath()
            self.dataPath_text.WriteText(self.DirPath)
        dialog.Destroy()

        # Actualizo la lista de archivos.
        self.GetFilesList()
        self.t2.Set(self.FileList)

    def onOutdirButton(self, event):
        """ Selecciono la carpeta donde estan los archivos a procesar """
        dialog = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.OutPath = dialog.GetPath()
            self.outPath_text.WriteText(self.OutPath)
        dialog.Destroy()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    window = Window()
    window.Show()
    app.MainLoop()
