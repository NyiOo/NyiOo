import  sys
from PyQt5.Qt import QColor
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import  QPainter, QPalette, QFont, QFontMetricsF, QPen, QPolygon
from PyQt5.QtCore import  Qt, QPoint, pyqtSignal, pyqtProperty


class CompassWidget(QWidget):

    angleChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super(CompassWidget, self).__init__(parent)
        self._angle=0.0
        self._margin=10
        self._pointText ={0: "0", 45: "45", 90: "90", 135: "135", 180: "180", 225: "225", 270: "270", 315: "315"}
        self.setFixedHeight(200)
        self.setFixedWidth(200) 


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), self.palette().brush(QPalette.Window))
        #painter.fillRect(event.rect(), Qt.black)
        self.drawMarkings(painter)
        self.drawNeedle(painter)

        painter.end()

    def drawMarkings(self,painter):
        painter.save()
        painter.translate(self.width()/2 , self.height()/2)
        scale = min((self.width() - self._margin)/120.0,
                    (self.height()- self._margin)/120.0)

        painter.scale(scale,scale)

        font = QFont(self.font())
        font.setPixelSize(10)
        metrics = QFontMetricsF(font)
        painter.setFont(font)
        painter.setPen(self.palette().color(QPalette.Shadow))
        #painter.setPen(Qt.red)
        # Draw Circle
        painter.drawEllipse(-50, -50, 100, 100)
        # Draw Marking (Line and Text)
        i=0
        while i <360:
            if i % 45==0:
                painter.drawLine(0,-40,0,-50)
                painter.drawText(-metrics.width(self._pointText[i])/2.0,-52,
                                 self._pointText[i])
            else:
                painter.drawLine(0, -43, 0, -50)

            painter.rotate(15)
            i += 15

        painter.restore()
        
        

    def drawNeedle(self,painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margin) / 120.0,
                    (self.height() - self._margin) / 120.0)

        painter.scale(scale, scale)

        painter.setPen(QPen(Qt.NoPen))

        painter.setBrush(self.palette().brush(QPalette.Highlight))

        #painter.setBrush(Qt.darkBlue)

        painter.drawPolygon(
            QPolygon([QPoint(0, 0), QPoint(-10, 10), QPoint(0,-40),
                      QPoint(10, 10), QPoint(0,0)])
        )

        painter.restore()

    # getter property
    def angle(self):
        return self._angle

    def setAngle(self,angle):
        if angle!= self._angle:
            self._angle = angle
            self.angleChanged.emit(angle)    # to use in Map
            self.update()

    # setter property and notify event
    angle = pyqtProperty(float,angle,setAngle)

def main():
    app = QApplication(sys.argv)
    window = CompassWidget()
    window.show()
    window.angle = 175
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
