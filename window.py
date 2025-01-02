
import sys
import subprocess

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt
from ui_MainWindow import MainWindow
from Direction_Finder.df_widget import DFWidget
from SpectrumAnalyzer.spectrum_widget import SpectrumWidget
from Radio.radio_widget import RadioWidget
from Map.map_widget import MapWidget


class MainWindow(QMainWindow, MainWindow):
    """QSpectrumAnalyzer main window"""
    def __init__(self, parent=None):
        # Initialize UI
        super().__init__(parent)
        self.setupUi(self)

        # DF Widget
        self.df_widget = DFWidget()
        self.verticalLayout_DF.addWidget(self.df_widget)
        self.verticalLayout_DF.setAlignment(Qt.AlignLeft)

        # Spectrum Widget
        self.spectrum_widget = SpectrumWidget(self.df_widget)
        self.verticalLayout_Spectrum.addWidget(self.spectrum_widget)
        
        # Radio Widget
        self.radio_widget = RadioWidget(self.df_widget)
        self.verticalLayout_analysis.addWidget(self.radio_widget)
        
        self.map_widget = MapWidget()
        self.verticalLayout_Map.addWidget(self.map_widget)
        self.df_widget.map = self.map_widget


        # Connections
        self.df_widget.signal_start.connect(self.close_spectrum_radio)
        self.spectrum_widget.spectrumPlotWidget.demodulation.triggered.connect(self.go_demodulation)
        self.spectrum_widget.spectrumPlotWidget.df.triggered.connect(self.go_DF)
        
        # Close Receivers
        self.close_x4_rtlsdr()

    def go_demodulation(self):
         freq = self.spectrum_widget.spectrumPlotWidget.freq
         self.spectrum_widget.stop()
         self.tabWidget.setCurrentIndex(1)
         self.radio_widget.frequency_spinbox.setValue(freq)
         #self.radio_widget.freq_assigned(freq)
         self.radio_widget.start()

    def go_DF(self):
        freq = self.spectrum_widget.spectrumPlotWidget.freq
        self.spectrum_widget.stop()
        self.tabWidget.setCurrentIndex(1)
        self.df_widget.doubleSpinBox_freq.setValue(freq)
        self.df_widget.receiver_reconfigure(freq)
        self.df_widget.start()

    def close_x4_rtlsdr(self):        
        self.df_widget.close_device()
#        self.df_widget.stop()

    def close_spectrum_radio(self):
        self.spectrum_widget.stop()
        self.radio_widget.close_device() 
        
    def closeEvent(self, QCloseEvent):        
        rc = subprocess.call("./kill.sh", shell=True)




def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
