try:
    from PyQt5 import Qt
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QWidget, QMainWindow, QHeaderView, QMessageBox
except ImportError:
    from PyQt4 import Qt,QtCore,QtGui
    from PyQt4.QtGui import QWidget,QMainWindow,QHeaderView, QMessageBox ,QDialog


import sys,os,time

currentpath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,currentpath)

from ui_RadioWidget import Radio_Form
import fft_display
import radio

class RadioWidget(QWidget, Radio_Form):    
    def __init__(self,df,parent=None):
        super().__init__(parent)
        Radio_Form.__init__(self)
        self.setupUi(self)
        
        self.df = df
        self.radio = radio.Radio(self)
        self.graphic_data = None
        self.read_config()

        self.initialize_controls()
        self.fft_widget = fft_display.FFTDispWidget(self, self.config)
        self.spectrum_layout.addWidget(self.fft_widget)

        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.start_btn_disable(False)

        self.mode_cmb.currentIndexChanged.connect(self.change_mode)
        self.gain_cmb.currentIndexChanged.connect(self.set_gain)
        self.frequency_spinbox.valueChanged.connect(self.freq_assigned)
        self.squelch_control.valueChanged[int].connect(self.set_squelch)
        self.agc_cmb.currentIndexChanged.connect(self.set_agc_mode)
        self.af_control.valueChanged[int].connect(self.set_af_gain)
        self.buttonGroup.buttonClicked.connect(self.set_bw_mode)


    def define_mode_list(self):
        self.mode_list = ['AM', 'FM', 'WFM', 'USB', 'LSB', 'CW_USB', 'CW_LSB']
        self.MODE_AM = 0
        self.MODE_FM = 1
        self.MODE_WFM = 2
        self.MODE_USB = 3
        self.MODE_LSB = 4
        self.MODE_CW_USB = 5
        self.MODE_CW_LSB = 6

    def define_agc_list(self):
        self.agc_list = ['SW/F', 'SW/S', 'HW', 'OFF']
        self.AGC_FAST = 0
        self.AGC_SLOW = 1
        self.AGC_HW = 2
        self.AGC_OFF = 3


    def initialize_controls(self):
        self.define_mode_list()
        self.define_agc_list()

        self.mode_cmb.addItems(self.mode_list)
        self.agc_cmb.addItems(self.agc_list)

        self.gain_list = [0, 0.9, 1.4, 2.7, 3.7, 7.7, 8.7, 12.5, 14.4, 15.7, 16.6, 19.7, 20.7, 22.9, 25.4, 28.0, 29.7,
                          32.8, 33.8, 36.4, 37.2, 38.6, 40.2, 42.1, 43.4, 43.9, 44.5, 48.0, 49.6]
        for val in self.gain_list:
            self.gain_cmb.addItem(str(val))

        self.gain_cmb.setCurrentIndex(7)
        self.squelch_control.setValue(self.radio.squelch_level)


    def get_default_config(self):
        defaults = {
            'af_gain': 356,
            'agc_mode': 0,
            'antenna': 0,
            'audio_rate': 52000,
            'average': 0.7525,
            'bandwidth': 20,
            'bw_mode': 0,
            'corr_ppm': 0,
            'corr_ppm_upc': 0,
            'cw_base': 750,
            'fft_size': 4096,
            'fft_zoom': 0,
            'frame_rate': 10,
            'freq': 88.6*1e6,
            'if_sample_rate': 240000,
            'gain': 12.5,
            'hilbert_taps': 128,
            'iq_balance': False,
            'dc_offset': False,
            'gain_mode':False,
            'mode': 1,
            'offset_freq': 0.0,
            'sample_rate': 2560000.0,
            'squelch_level': -100,
            'dbscale_hi': 10,
            'dbscale_lo': -140,
            'disp_text_color': '#80c0ff',
            'disp_trace_color': '#ffff00',
            'disp_vline_color': '#c00000',

        }
        return defaults

    def read_config(self):
        self.config = self.get_default_config()
        self.radio.sample_rate = self.config['sample_rate']
        self.radio.audio_rate = self.config['audio_rate']
        self.radio.if_sample_rate = self.config['if_sample_rate']
        self.radio.ssb_hi = 3000
        self.radio.ssb_lo = 100
        self.radio.hilbert_taps_ssb = self.config['hilbert_taps']
        self.radio.cw_base = self.config['cw_base']
        self.radio.cw_lo = -self.radio.cw_base / 2
        self.radio.cw_hi = self.radio.cw_base / 2
        self.radio.squelch_level = self.config['squelch_level']
        self.radio.fc = self.config['freq']
        self.radio.corr_ppm = self.config['corr_ppm']
        self.radio.dc_offset_mode = self.config['dc_offset']
        self.radio.iq_balance_mode = self.config['iq_balance']
        self.radio.gain_mode = self.config['gain_mode']
        self.radio.gain = self.config['gain']
        self.radio.bandwidth = self.config['bandwidth'] * 1e3
        self.radio.mode = self.config['mode']
        self.radio.fft_size = self.config['fft_size']
        self.radio.frame_rate = self.config['frame_rate']
        self.radio.average = self.config['average']



    def change_mode(self):
        self.radio.mode = self.mode_cmb.currentIndex()
        if self.radio.osmosdr_source != None:
            self.stop()
            self.start()
            
    def freq_assigned(self,value):
        f = value * 1e6
        self.freq_changed(f)

    def freq_changed(self,value):
        self.radio.fc = value
        if self.radio.osmosdr_source != None:
            self.radio.osmosdr_source.set_center_freq(int(self.radio.fc), 0)
            self.radio.osmosdr_source.set_freq_corr(self.radio.corr_ppm, 0)
        self.radio.update_freq_xlating_fir_filter()

    def set_af_gain(self, value):
        if self.radio.blocks_multiply_const_volume != None:
            # use a power function to control volume levels
            result = self.radio.ntrp(value, 0.0, 400, 0, 1)
            y = 2 * result * result
            self.radio.blocks_multiply_const_volume.set_k((y,))

    def set_squelch(self, value):
        result = self.radio.ntrp(value, 0.0, 400, -130, 50)
        if self.radio.analog_pwr_squelch != None:
            self.radio.analog_pwr_squelch.set_threshold(result)
        if self.radio.analog_pwr_squelch_ssb != None:
            self.radio.analog_pwr_squelch_ssb.set_threshold(result)

    def set_gain(self, value):
        self.radio.gain = value
        if self.radio.osmosdr_source != None :
            self.radio.osmosdr_source.set_gain(value,0)

    def set_bandwidth(self):
        self.radio.bandwidth = float(self.bandwidth_cmb.currentText())
        if self.radio.osmosdr_source != None :
            self.radio.osmosdr_source.set_bandwidth(self.radio.bandwidth,0)

    def set_bw_mode(self, button):
        txt = button.text()
        if txt == 'M':
            value = 1
        elif txt == 'N':
            value = 2
        else:
            value = 0
        self.radio.rebuild_filters(value)

    def set_agc_mode(self, mode=None):
        if mode == None:
            mode = self.config['agc_mode']
        if self.radio.osmosdr_source != None:
            hw_mode = False
            agc_reference = 1
            agc_gain = 1
            agc_max_gain = 1
            agc_attack_rate = 1e-1
            agc_decay_rate = 1e-1
            if mode == self.AGC_SLOW:
                agc_decay_rate = 1e-3
                agc_max_gain = 65536
            elif mode == self.AGC_FAST:
                agc_max_gain = 65536
            elif mode == self.AGC_HW:
                hw_mode = True
            self.radio.osmosdr_source.set_gain_mode(hw_mode, 0)
            if self.radio.analog_agc_cc != None:
                # print("setting AGC mode: %d" % mode)
                for inst in (self.radio.analog_agc_cc, self.radio.analog_agc_ff):
                    inst.set_reference(agc_reference)
                    inst.set_gain(agc_gain)
                    inst.set_max_gain(agc_max_gain)
                    inst.set_attack_rate(agc_attack_rate)
                    inst.set_decay_rate(agc_decay_rate)


    def Message(self,title,msg):
        ms = QMessageBox(QMessageBox.Warning, title, msg, QMessageBox.Ok)
        ms.exec_()

    def start(self):        
        self.df.close_device()
        self.radio.osmosdr_source = None
        self.radio.initialize_radio()
        if not self.radio.error:
            self.start_btn_disable(True)
            self.radio.start()


    def stop(self):
        self.radio.stop()
        self.radio.wait()
        self.radio.disconnect_all()
        self.start_btn_disable(False)

    def close_device(self):        
        self.radio.osmosdr_source = None
        del self.radio.osmosdr_source

    def start_btn_disable(self, flag):
        self.start_btn.setEnabled(not flag)
        self.stop_btn.setEnabled(flag)

    def draw_fft_disp(self):
        if self.graphic_data != None:
            # sya = self.config['dbscale_lo']
            # syb = self.config['dbscale_hi']
            # note Y axis reversal
            self.fft_widget.accept_data(self.graphic_data)
            self.graphic_data = None


if __name__=='__main__':
    app = Qt.QApplication(sys.argv)
    form = RadioWidget()
    form.show()
    sys.exit(app.exec_())