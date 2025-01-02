import sys
import os
import subprocess
import math
import numpy as np
import scipy
import time
import pyqtgraph as pg


from PyQt5.QtWidgets import QProgressBar, QWidget, QApplication
from PyQt5.QtCore import QThreadPool, Qt, pyqtSignal


currentpath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,currentpath)
receiverpath= os.path.join(currentpath,"_receiver")
sys.path.insert(0,receiverpath)

from  compass_widget import CompassWidget
from background_worker import Worker
from ui_DFWidget import DF_Form
from hydra_signal_processor import SignalProcessor
from hydra_receiver import ReceiverRTLSDR

import pyqtgraph as pg
import serial


class DFWidget(QWidget , DF_Form):
    signal_start = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.center_freq = None
        self.gain = None
        self.bw = None
        self.antenna_space = None
        self.stop_flag = False
        self.close_flag = False
        self.spectrum_flag = False
        self.antenna_values = None

        self.create_spectrum()
        self.create_compass()
        self.create_progressbar()

        self.module_receiver = ReceiverRTLSDR()
        self.module_receiver.block_size = int(sys.argv[1]) * 1024
#        self.module_receiver.block_size = 256 * 1024
        self.module_signal_processor = SignalProcessor(module_receiver=self.module_receiver)
        
#        self.InitializeSyncDisplay()
#        self.sample_phase_plot()
        self.initialize_combobox()
        self.pushButton_stop.setEnabled(False)

        # Connections...
        self.module_signal_processor.signal_DOA_ready.connect(self.DOA_plot)
        self.module_receiver.signal_spectrum_ready.connect(self.spectrum_plot)
#        self.module_signal_processor.signal_sync_ready.connect(self.delay_plot)
        self.module_signal_processor.signal_progressbar.connect(self.progressbar_changed)

        self.pushButton_start.clicked.connect(self.start)
        self.pushButton_stop.clicked.connect(self.stop)
#        self.pushButton_test.clicked.connect(self.close_device)
        self.doubleSpinBox_freq.valueChanged.connect(self.on_value_changed)
        self.doubleSpinBox_freq.valueChanged.connect(self.calculate_antenna_distance)
        self.doubleSpinBox_bandwidth.valueChanged.connect(self.on_value_changed)
        self.comboBox_gain.currentIndexChanged.connect(self.on_value_changed)

        # Thread Pool
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        
        self.doubleSpinBox_freq.setProperty("value", 362.175)

    def create_spectrum(self):
        self.win_spectrum = pg.GraphicsWindow(title="")
        self.win_spectrum.resize(350, 300)
        self.plotWidget_spectrum = self.win_spectrum.addPlot(title="")
        self.channel_VLayout.addWidget(self.win_spectrum)

        x = np.arange(1000)
        y = np.random.normal(size=(4, 1000))

        self.spectrum_curve = self.plotWidget_spectrum.plot(x, y[0], clear=True, pen=(255, 199, 15))
        self.plotWidget_spectrum.setLabel("bottom", "Frequency [MHz]")
        self.plotWidget_spectrum.setLabel("left", "Amplitude [dBm]")

    def create_compass(self):
        self.compass = CompassWidget()
        self.compass_VLayout.addWidget(self.compass)

    def create_progressbar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.progressBar.setObjectName("progressBar")
        self.compass_VLayout.addWidget(self.progressBar)

    def start(self):
        self.signal_start.emit()             
        time.sleep(0.5) 
        self.module_receiver.open_device()
        self.pushButton_stop.setEnabled(True)
        self.pushButton_start.setEnabled(False)
        
#        self.stop_flag = False
#        self.module_signal_processor.start()
       
        if self.stop_flag:
            self.progressBar.setValue(0)
            self.receiver_reconfigure()
            self.default_configure()
            self.module_signal_processor.start()
            # Background Worker
            worker = Worker(self.synchronization)
            self.threadpool.start(worker)
            worker.signals.finished.connect(self.finished_task)
            worker.signals.progressed.connect(self.progressbar_changed)
        else:
            self.finished_task()

        self.close_flag = False
        self.spectrum_flag = True


    def stop(self):
        self.module_signal_processor.en_DOA_estimation = False       
        self.pushButton_stop.setEnabled(False)
        self.pushButton_start.setEnabled(True)
        
        self.stop_flag = False
        self.spectrum_flag = False
        

    def close_device(self):
        if not self.close_flag:
            self.module_signal_processor.en_DOA_estimation = False   
            self.module_signal_processor.stop()
            self.module_receiver.close_device()
            self.stop_flag = True
            self.close_flag = True
      

    def closeEvent(self, QCloseEvent):
        self.module_receiver.close()


    def calculate_antenna_spacing(self,freq):        
        wave_length = (299.79 / freq)
        ant_meters = (wave_length*0.45)/ math.sqrt(2)
        ant_spacing = ((ant_meters / wave_length) / math.sqrt(2))
        return (ant_meters,ant_spacing)

    def receiver_reconfigure(self, freq=None):
        if freq is None:
            self.center_freq = self.doubleSpinBox_freq.value() * 10 ** 6
        else:
            self.center_freq = freq * 1e6

        gain = [0, 0, 0, 0]
        for i in range(4):
            gain[i] = 10 * 15.7

        self.module_signal_processor.fs = self.module_receiver.fs / self.module_receiver.decimation_ratio
        self.module_signal_processor.center_freq = self.center_freq
        self.module_signal_processor.DOA_inter_elem_space = round(self.antenna_values[1],3)
        self.module_receiver.reconfigure_tuner(self.center_freq, self.module_receiver.fs, gain)
        
        
    def default_configure(self):
        bw= 100 *10**3
        tap_size = 0
        self.module_receiver.set_fir_coeffs(tap_size, bw)
        self.module_receiver.decimation_ratio = 1

    def synchronization(self, progress_callback):
        progress_callback.emit(1)       
        #self.serial = serial.Serial('/dev/ttyACM0',9600)
        time.sleep(2)
        #self.serial.write(b'H')
        
        time.sleep(2)
        self.module_receiver.switch_noise_source(1)
        progress_callback.emit(20)
        time.sleep(2)
        self.module_signal_processor.en_sync = True
        progress_callback.emit(40)
        time.sleep(1)
        self.sample_offset_calculate()
        progress_callback.emit(50)
        time.sleep(2)
        self.iq_calibrate()
        progress_callback.emit(70)
        time.sleep(3)
        self.after_synchronization()
        progress_callback.emit(90)       

    def sample_offset_calculate(self):

        self.module_signal_processor.en_sample_offset_sync = True

    def iq_calibrate(self):
        self.module_signal_processor.en_calib_iq = True

    def after_synchronization(self):
        self.module_receiver.switch_noise_source(0)
        self.module_signal_processor.en_sync = False
        
    def configure_iq(self):
        tap_size = 100
        bw = self.doubleSpinBox_bandwidth.value() * 10 ** 3  # ->[kHz]
        self.module_receiver.set_fir_coeffs(tap_size, bw)
        self.module_receiver.decimation_ratio = 4

    def DF_Enable(self):
        if self.stop_flag:
            self.configure_iq()
            time.sleep(1)
        self.module_signal_processor.en_DOA_estimation = True        

    def progressbar_changed(self, value):
        self.progressBar.setValue(value)

    def finished_task(self):
        self.DF_Enable()
        self.progressBar.setValue(100)        
        
        #self.serial.write(b'L')
        #self.serial.close()

    def result_diplay(self, *args):

        self.label_azimuth.setText(str(round(args[0],2)) + u"\u00b0")
        self.label_amplitude.setText(str(round(args[1], 3)) + ' dBm')
        self.label_confidence.setText(str(round(args[2], 1)))

    def initialize_combobox(self):
        gain_lst = [0, 0.9, 1.4, 2.7, 3.7, 7.7, 8.7, 12.5, 14.4, 15.7, 16.6, 19.7, 20.7, 22.9, 25.4, 28.0, 29.7, 32.8,
                    33.8, 36.4,
                    37.2, 38.6, 40.2, 42.1, 43.4, 43.9, 44.5, 48.0, 49.6]
        for value in gain_lst:
            self.comboBox_gain.addItem(str(value))

        self.comboBox_gain.setCurrentIndex(3)

    def on_value_changed(self, value):
        self.stop_flag = True
        
    def calculate_antenna_distance(self,freq):
        self.antenna_values = self.calculate_antenna_spacing(freq)
        self.label_meter.setText(str(round(self.antenna_values[0],3)))
        

    def initialize_values(self):
        self.center_freq = self.doubleSpinBox_freq.value()
        self.gain = float(self.comboBox_gain.currentText())
        self.bw = self.doubleSpinBox_bandwidth.value()
        self.antenna_space = self.doubleSpinBox_antenna_space.value()

    def DOA_plot_helper(self, DOA_data, incident_angles, log_scale_min=None, color=(255, 199, 15), legend=None):

        DOA_data = np.divide(np.abs(DOA_data), np.max(np.abs(DOA_data)))  # normalization
        if (log_scale_min != None):
            DOA_data = 10 * np.log10(DOA_data)
            theta_index = 0
            for theta in incident_angles:
                if DOA_data[theta_index] < log_scale_min:
                    DOA_data[theta_index] = log_scale_min
                theta_index += 1
#        plot = self.plotWidget_DOA.plot(incident_angles, DOA_data, pen=pg.mkPen(color, width=2))

        return DOA_data

    def DOA_plot(self):

        thetas = self.module_signal_processor.DOA_theta

        MUSIC = self.module_signal_processor.DOA_MUSIC_res

        DOA = 0
        DOA_results = []
        COMBINED = np.zeros_like(thetas, dtype=np.complex)

#        self.plotWidget_DOA.clear()

        self.DOA_plot_helper(MUSIC, thetas, log_scale_min=-50, color=(9, 237, 237))
        COMBINED += np.divide(np.abs(MUSIC), np.max(np.abs(MUSIC)))
        # de.DOA_plot(MUSIC, thetas, log_scale_min = -50, axes=self.axes_DOA)
        DOA_results.append(thetas[np.argmax(MUSIC)])

        # COMBINED_LOG = 10*np.log10(COMBINED)

        if len(DOA_results) != 0:

            # Combined Graph (beta)
            COMBINED_LOG = self.DOA_plot_helper(COMBINED, thetas, log_scale_min=-50, color=(163, 64, 245))

            confidence = scipy.signal.find_peaks_cwt(COMBINED_LOG, np.arange(10, 30),
                                                     min_snr=1)  # np.max(DOA_combined**2) / np.average(DOA_combined**2)
            maxIndex = confidence[np.argmax(COMBINED_LOG[confidence])]
            confidence_sum = 0;

            # print("Peaks: " + str(confidence))
            for val in confidence:
                if (val != maxIndex and np.abs(COMBINED_LOG[val] - min(COMBINED_LOG)) > np.abs(
                        min(COMBINED_LOG)) * 0.25):
                    # print("Doing other peaks: " + str(val) + "combined value: " + str(COMBINED_LOG[val]))
                    confidence_sum += 1 / (np.abs(COMBINED_LOG[val]))
                elif val == maxIndex:
                    # print("Doing maxIndex peak: " + str(maxIndex) + "min combined: " + str(min(COMBINED_LOG)))
                    confidence_sum += 1 / np.abs(min(COMBINED_LOG))
            # Get avg power level
            max_power_level = np.max(self.module_signal_processor.spectrum[1, :])
            # rms_power_level = np.sqrt(np.mean(self.module_signal_processor.spectrum[1,:]**2))

            confidence_sum = 10 / confidence_sum

            # print("Max Power Level" + str(max_power_level))
            # print("Confidence Sum: " + str(confidence_sum))

            DOA_results = np.array(DOA_results)
            # Convert measured DOAs to complex numbers
            DOA_results_c = np.exp(1j * np.deg2rad(DOA_results))
            # Average measured DOA angles
            DOA_avg_c = np.average(DOA_results_c)
            # Convert back to degree
            DOA = np.rad2deg(np.angle(DOA_avg_c))

            # Update DOA results on the compass display
            # print("[ INFO ] Python GUI: DOA results :",DOA_results)
            if DOA < 0:
                DOA += 360
            DOA = 360 - DOA

            self.compass.angle = DOA
            self.map.SetAngle(int(DOA),0)  

            self.result_diplay(DOA, max_power_level, confidence_sum)

    def InitializeSyncDisplay(self):
        # ---> Sync display <---
        # --> Delay

        self.win_sync = pg.GraphicsWindow(title="Receiver Sync")

        self.plotWidget_sync_absx = self.win_sync.addPlot(title="ABS X Corr")

        # Frequency Curve
        self.plotWidget_spectrum = self.win_sync.addPlot(title="Channel 1")

        x = np.arange(1000)
        y = np.random.normal(size=(4, 1000))

        self.spectrum_curve = self.plotWidget_spectrum.plot(x, y[0], clear=True, pen=(255, 199, 15))

        self.win_sync.nextRow()

        self.plotWidget_sync_sampd = self.win_sync.addPlot(title="Sample Delay History")
        self.plotWidget_sync_phasediff = self.win_sync.addPlot(title="Phase Diff History")

        self.win_sync.nextRow()

        self.plotWidget_DOA = self.win_sync.addPlot(title="Direction of Arrival Estimation")
        self.plotWidget_DOA.setLabel("bottom", "Incident Angle [deg]")
        self.plotWidget_DOA.setLabel("left", "Amplitude [dB]")
        self.plotWidget_DOA.showGrid(x=True, alpha=0.25)

        self.plotWidget_DOA.addLegend()
        self.plotWidget_DOA.plot(x, y[3], pen=pg.mkPen((9, 237, 237), width=2), name="MUSIC")

        self.gridLayout_sync.addWidget(self.win_sync, 1, 1, 1, 1)
        
    def sample_phase_plot(self):
        self.win_sync = pg.GraphicsWindow(title="Receiver Sync")
        self.plotWidget_sync_absx = self.win_sync.addPlot(title="ABS X Corr")
        self.plotWidget_sync_sampd = self.win_sync.addPlot(title="Sample Delay History")
        self.plotWidget_sync_phasediff = self.win_sync.addPlot(title="Phase Diff History")
        self.gridLayout_sync.addWidget(self.win_sync, 1, 1, 1, 1)
        

    def delay_plot(self):
        xcorr12 = 10 * np.log10(np.abs(self.module_signal_processor.xcorr[0, :]))
        xcorr13 = 10 * np.log10(np.abs(self.module_signal_processor.xcorr[1, :]))
        xcorr14 = 10 * np.log10(np.abs(self.module_signal_processor.xcorr[2, :]))

        N = np.size(xcorr12) // 2

        xcorr12 -= np.max(xcorr12)
        xcorr13 -= np.max(xcorr13)
        xcorr14 -= np.max(xcorr14)

        M = 500
        max_delay = np.max(np.abs(self.module_signal_processor.delay_log[:, -1]))
        if max_delay + 50 > M:
            M = max_delay + 50

        delay_label = np.arange(-M, M + 1, 1)

        self.plotWidget_sync_absx.clear()

        self.plotWidget_sync_absx.plot(delay_label, xcorr12[N - M:N + M + 1], pen=(255, 199, 15))
        self.plotWidget_sync_absx.plot(delay_label, xcorr13[N - M:N + M + 1], pen='r')
        self.plotWidget_sync_absx.plot(delay_label, xcorr14[N - M:N + M + 1], pen='g')

        # Plot delay history

        self.plotWidget_sync_sampd.clear()

        self.plotWidget_sync_sampd.plot(self.module_signal_processor.delay_log[0, :], pen=(255, 199, 15))
        self.plotWidget_sync_sampd.plot(self.module_signal_processor.delay_log[1, :], pen='r')
        self.plotWidget_sync_sampd.plot(self.module_signal_processor.delay_log[2, :], pen='g')

        # Plot phase history

        self.plotWidget_sync_phasediff.clear()

        self.plotWidget_sync_phasediff.plot(self.module_signal_processor.phase_log[0, :], pen=(255, 199, 15))
        self.plotWidget_sync_phasediff.plot(self.module_signal_processor.phase_log[1, :], pen='r')
        self.plotWidget_sync_phasediff.plot(self.module_signal_processor.phase_log[2, :], pen='g')

    def spectrum_plot(self):
        if self.module_receiver.spectrum_samples is not None:
            iq_samples = self.module_receiver.spectrum_samples[0:(2**14)]
            if self.spectrum_flag:
                freqs = np.fft.fftshift(np.fft.fftfreq((2**14), 1/ (1.024 * 10**6))) / 10 ** 6
                xw1 = 10 * np.log10(np.fft.fftshift(np.abs(np.fft.fft(iq_samples))))
                self.spectrum_curve.setData(freqs, xw1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DFWidget()
    window.show()
    sys.exit(app.exec())