import  math
try:
    from PyQt5 import QtCore
    from PyQt5.QtCore import Qt, QPointF
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except ImportError:
    try:
        from PyQt4.QtGui import *
        from PyQt4 import QtCore
        from PyQt4.QtCore import pyqtSignal
    except ImportError:
        raise ImportError("QtImageViewer: Requires PyQt5 or PyQt4.")

class Station(QGraphicsEllipseItem):
    def __init__(self, top_left_x, top_left_y, index, radius, name, coordinates):
        super().__init__(top_left_x, top_left_y, radius, radius)
        self.name = name
        self.index = index
        self.x = top_left_x
        self.y = top_left_y
        self.coordinates = coordinates

        # DF Line
        self.DF = None
        # self.pen = QPen(QColor(255, 0, 0), 2, QtCore.Qt.SolidLine)
        self.pen = QPen(Qt.green, 5, Qt.SolidLine)

        # Station Name
        self.text = QGraphicsTextItem()
        self.text.setFont(QFont('Arial', 48))
        self.text.setPos(self.x, self.y + 55)
        self.text.setPlainText(self.name)

        if self.index == 0:
            self.setBrush(Qt.green)
            self.text.setDefaultTextColor(Qt.green)
        else:
            self.setBrush(Qt.yellow)
            self.text.setDefaultTextColor(Qt.yellow)

    def DrawDFLine(self, angle):
        rad = angle * (math.pi / 180)
        if self.DF is None:
            self.DF = QGraphicsLineItem()
            rect = self.boundingRect()
            center = rect.center()
            self.cx = center.x()
            self.cy = center.y()

        x1 = 3000 * math.sin(rad) + self.cx
        y1 = self.cy - (3000 * math.cos(rad))
        self.DF.setLine(self.cx, self.cy, x1, y1)
        self.DF.setPen(self.pen)

        return self.DF

    def SetPosition(self, x, y, coord):
        mx = x - self.x
        my = y - self.y
        self.x = x
        self.y = y
        self.cx = self.x + 25
        self.cy = self.y + 25
        self.coordinates = coord
        self.moveBy(mx, my)
        self.text.moveBy(mx, my)






