import traceback,sys
from PyQt5.QtCore import QRunnable , pyqtSignal ,QObject


class WorkerSignal(QObject):
    finished = pyqtSignal()
    progressed = pyqtSignal(int)
    error = pyqtSignal(tuple)


class Worker(QRunnable):
    def __init__(self,fn,*args,**kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignal()
        self.kwargs['progress_callback'] = self.signals.progressed

    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype,value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()




