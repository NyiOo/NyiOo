
import random
try:
    from PyQt5.QtCore import pyqtSignal,QThread
except ImportError:
    from PyQt4.QtCore import pyqtSignal, QThread


class DegGenQThread(QThread):
    drawlinecommand = pyqtSignal(int,int)

    def __init__(self,parent=None):
        super(DegGenQThread, self).__init__(parent)
        self.runs = True

    def run(self):

        while self.runs:
            degree = random.randint(0, 360)
            self.sleep(2)
            self.drawlinecommand.emit(degree,0)

    def stop(self):
        self.runs = False











