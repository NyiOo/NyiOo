import sys, signal, time, os
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget ,QApplication, QMessageBox

currentpath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,currentpath)

from rtl_power import Info,PowerThread
from data import DataStorage
from plot import SpectrumPlotWidget, WaterfallPlotWidget
from ui_SpectrumWidget import Spectrum_Form


# Allow CTRL+C and/or SIGTERM to kill us (PyQt blocks it otherwise)
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

class SpectrumWidget(QWidget, Spectrum_Form): 
    def __init__(self,df):
        super().__init__()
        self.setupUi(self)
        self.df = df
        # Create plot widgets and update UI
        self.spectrumPlotWidget = SpectrumPlotWidget(self.mainPlotLayout)
        self.waterfallPlotWidget = WaterfallPlotWidget(self.waterfallPlotLayout)

        # Link main spectrum plot to waterfall plot
        self.spectrumPlotWidget.plot.setXLink(self.waterfallPlotWidget.plot)

        # Setup power thread and connect signals
        self.prev_data_timestamp = None
        self.data_storage = None
        self.power_thread = None
        self.backend = None
        self.setup_power_thread()

        self.update_buttons()
        self.load_settings()

    def setup_power_thread(self):
        """Create power_thread and connect signals to slots"""
        if self.power_thread:
            self.stop()

        self.data_storage = DataStorage(100)
        self.data_storage.data_updated.connect(self.spectrumPlotWidget.update_plot)
        self.data_storage.history_updated.connect(self.waterfallPlotWidget.update_plot)

        self.startFreqSpinBox.setMinimum(Info.start_freq_min)
        self.startFreqSpinBox.setMaximum(Info.start_freq_max)
        self.startFreqSpinBox.setValue(Info.start_freq)
        self.stopFreqSpinBox.setMinimum(Info.stop_freq_min)
        self.stopFreqSpinBox.setMaximum(Info.stop_freq_max)
        self.stopFreqSpinBox.setValue(Info.stop_freq)
        self.gainSpinBox.setMinimum(Info.gain_min)
        self.gainSpinBox.setMaximum(Info.gain_max)
        self.gainSpinBox.setValue(Info.gain)

        # Setup default values and limits in case that LNB LO is changed
        lnb_lo = float(0.0) / 1e6
        start_freq_min = Info.start_freq_min + lnb_lo
        start_freq_max = Info.start_freq_max + lnb_lo
        start_freq = self.startFreqSpinBox.value()
        stop_freq_min = Info.stop_freq_min + lnb_lo
        stop_freq_max = Info.stop_freq_max + lnb_lo
        stop_freq = self.stopFreqSpinBox.value()

        self.startFreqSpinBox.setMinimum(start_freq_min if start_freq_min > 0 else 0)
        self.startFreqSpinBox.setMaximum(start_freq_max)
        if start_freq < start_freq_min or start_freq > start_freq_max:
            self.startFreqSpinBox.setValue(start_freq_min)

        self.stopFreqSpinBox.setMinimum(stop_freq_min if stop_freq_min > 0 else 0)
        self.stopFreqSpinBox.setMaximum(stop_freq_max)
        if stop_freq < stop_freq_min or stop_freq > stop_freq_max:
            self.stopFreqSpinBox.setValue(stop_freq_max)

        self.power_thread = PowerThread(self.data_storage)
        self.power_thread.powerThreadStarted.connect(self.update_buttons)
        self.power_thread.powerThreadStopped.connect(self.update_buttons)

    def load_settings(self):
        """Restore spectrum analyzer settings and window geometry"""

        self.startFreqSpinBox.setValue(87.0)
        self.stopFreqSpinBox.setValue(108.0)
        self.gainSpinBox.setValue(0)

        self.show()

    def update_buttons(self):
        """Update state of control buttons"""
        self.pushButton_stop.setEnabled(self.power_thread.alive)
        self.pushButton_start.setEnabled(not self.power_thread.alive)



    def start(self, single_shot=False):
        """Start power thread"""
        self.prev_data_timestamp = time.time()

        self.data_storage.reset()
        self.data_storage.set_smooth(bool(1), 11, "hanning", recalculate=False)

        self.waterfallPlotWidget.history_size = 100
        self.waterfallPlotWidget.clear_plot()

        if not self.power_thread.alive:
            self.power_thread.setup(float(self.startFreqSpinBox.value()),
                                    float(self.stopFreqSpinBox.value()),
                                    10.0,
                                    interval= 0.1,
                                    gain=self.gainSpinBox.value(),
                                    ppm=0,
                                    crop= 30 / 100.0,
                                    single_shot=single_shot,
                                    device="0",    # 0
                                    sample_rate=2560000.0,
                                    bandwidth=0.0,
                                    lnb_lo=0.0)
            self.power_thread.start()

    
    def stop(self):
        """Stop power thread"""
        if self.power_thread.alive:
            self.power_thread.stop()
   

    @pyqtSlot()
    def on_pushButton_start_clicked(self):
        self.df.close_device()
#        self.df.stop()
        if self.checkFreq():
            self.start()
        else:
            ms = QMessageBox(QMessageBox.Warning,'Limit Exceed!!','Bandwidth should not be greater than 20 MHz',QMessageBox.Ok)
            ms.exec_()

    @pyqtSlot()
    def on_pushButton_stop_clicked(self):
        self.stop()
        
    def checkFreq(self):
        f1 = float(self.startFreqSpinBox.value())
        f2 = float(self.stopFreqSpinBox.value())
        if f1 < f2:
            delta = f2 - f1
            if delta <= 20:
                return True
            else:
                return False
        else:
            return False

    def closeEvent(self, event):
        self.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpectrumWidget()
    window.show()
    sys.exit(app.exec())