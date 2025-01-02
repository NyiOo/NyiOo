try:
    from PyQt5 import QtCore
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4 import QtCore


from Map.MultiPageTIFFViewerQt import MultiPageTIFFViewerQt
from Map.Station import Station
#from Map.BackgroundThread import DegGenQThread
import rasterio
import configparser

class PlugIn:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(r'/home/pi/TaSaKha/config.ini')
        self.map_path = config.get('default','map_path')
        lat = config.get('default', 'latitude')
        long = config.get('default', 'longitude')
        name = config.get('default', 'device')

        self.stackviewer = MultiPageTIFFViewerQt()
        self.stackviewer.loadImageStackFromFile(self.map_path)


        # Create Dataset for coordinate calculation
        self.stackviewer.CreateDataSet()
        self.dataset = rasterio.open(self.map_path)

        self.stations = []
        for x in [1, 2, 3, 4]:
            self.stations.append(None)

        # Draw Ellipse Item For Kerberossdr
        x, y = self.convertRowColumn(long, lat)
        self.stations[0] = Station(x, y, 0, 50, name, (long, lat))
        self.stackviewer.viewer.scene.addItem(self.stations[0])
        self.stackviewer.viewer.scene.addItem(self.stations[0].text)


        #Draw True North
        image = QPixmap(r'E:\compass.png')
        scaled_img = image.scaled(500,500,QtCore.Qt.KeepAspectRatio)
        item = self.stackviewer.viewer.scene.addPixmap(scaled_img)
        item.setPos(self.dataset.width-500, 0)


#        self.df_random = DegGenQThread()
#        self.df_random.drawlinecommand.connect(self.setAngle)
#        self.df_random.start()

    def graphicViewer(self):
        return self.stackviewer

    def convertRowColumn(self, lon, lat):
        col, row = self.dataset.index(float(lon), float(lat))
        return row, col

    def convertBackData(self, index):
        station = self.stations[index]
        if isinstance(station, QGraphicsEllipseItem):
            #x, y = self.dataset.xy(station.x+25, station.y+25 )
            x, y = station.coordinates
            n = station.name
            return x, y, n
        else:
            return '','',''

    def setStation(self, x, y, index, name):
        if index < 4:
            coordinates = (x,y)
            row, col = self.convertRowColumn(x, y)
            flag = self.checkStations(row-25, col-25, index, name)
            if flag == 0:
                return
            elif flag == 1:
                self.stations[index].text.setPlainText(name)
            elif flag == 2:
                self.stations[index].SetPosition(row-25, col-25, coordinates)
                self.stackviewer.viewer.scene.removeItem(self.stations[index].DF)
            else:
                self.stations[index] = Station(row-25, col-25, index, 50, name, coordinates)
                self.stackviewer.viewer.scene.addItem(self.stations[index])
                self.stackviewer.viewer.scene.addItem(self.stations[index].text)

        self.stackviewer.viewer.scene.update()


    def setAngle(self, angle, index):
        DF = self.stations[index].DrawDFLine(angle)
        items =  self.stackviewer.viewer.scene.items()
        print(len(items))
        self.stackviewer.viewer.scene.addItem(DF)


    def checkStations(self, x, y, index, name):
        station = self.stations[index]
        if isinstance(station, Station):
            if station.x == x and station.y == y:
                if station.name == name:
                    return 0
                else:
                    return 1
            else:
                return 2
        else:
            return 3

    def deleteDFLine(self, df):
        items = self.stackviewer.viewer.scene.items()
        for item in items:
            if isinstance(item, QGraphicsLineItem):
                if item == df:
                    self.stackviewer.viewer.scene.removeItem(df)
                    return



    def CurrentStation(self, index):
        station = self.stations[index]
        if isinstance(station, QGraphicsEllipseItem):
            self.stackviewer.viewer.scene.removeItem(station)
            self.stackviewer.viewer.scene.removeItem(station.DF)
            self.stackviewer.viewer.scene.removeItem(station.text)
            self.stations[index] = None

