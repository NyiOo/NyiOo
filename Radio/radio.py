import sys
path_gnu ="/usr/local/lib/python3/dist-packages"
sys.path.insert(0,path_gnu)

try:
    from PyQt5 import QtCore
    from PyQt5 import QtGui
    from PyQt5.QtWidgets import QWidget
except ImportError:
    from PyQt4 import Qt,QtCore,QtGui
    from PyQt4.QtGui import QWidget,QMainWindow,QHeaderView, QMessageBox ,QDialog
    from PyQt4.QtCore import pyqtSlot
    

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
from gnuradio import filter
from gnuradio.fft import logpwrfft
import osmosdr

import numpy as np

class DrawGraphics(QtCore.QObject):
    draw = QtCore.pyqtSignal()

# a convenience class to acquire data from Gnuradio

class MyVectorSink(gr.sync_block):
    def __init__(self, main, sz):
        self.main = main
        self.sz = sz

        gr.sync_block.__init__(
            self,
            name="My Vector sink",
            in_sig=[(np.float32, self.sz)],
            out_sig=None,
        )
        # event-related
        self.drawgr = DrawGraphics()
        self.drawgr.draw.connect(self.main.draw_fft_disp)

    def work(self, input_items, output_items):
        if (self.main.graphic_data == None):
            data = np.fft.fftshift(input_items)
            self.main.graphic_data = data[0][0].tolist()
            self.drawgr.draw.emit()
        return len(input_items)

class Radio(gr.top_block,QWidget):
    def __init__(self,main):
        gr.top_block.__init__(self, "Top Block")
        QWidget.__init__(self)

        self.main = main

        ##################################################
        # Variables
        ##################################################
        self.sample_rate = 0
        self.audio_rate = 0
        self.if_sample_rate = 0  #int(240e3)
        self.ssb_hi = 0
        self.ssb_lo = 0
        self.hilbert_taps_ssb = 0
        self.cw_base = 0
        self.cw_lo = 0
        self.cw_hi = 0
        self.cw_offset = 0
        self.squelch_level = 0
        self.fc = 0
        self.corr_ppm = 0
        self.dc_offset_mode = 0
        self.iq_balance_mode = 0
        self.gain_mode = False
        self.gain = 0
        self.bandwidth = 0
        self.mode = 0
        self.fft_size = 0
        self.frame_rate = 0
        self.average = 0
        self.error = False

        self.fir_offset_f = self.limit_offset_range(self.fc, self.audio_rate / 2)
        self.blocks_multiply_const_volume = None
        self.logpwrfft = None
        self.audio_sink = None
        self.osmosdr_source = None
        self.analog_agc_cc = None
        self.analog_pwr_squelch = None
        self.analog_pwr_squelch_ssb = None
        self.freq_xlating_fir_filter = None
        self.low_pass_filter_am = None
        self.low_pass_filter_fm = None
        self.low_pass_filter_wfm = None
        self.low_pass_filter_ssb = None
        self.band_pass_filter_cw = None

    def initialize_radio(self):
        self.configure_source()
        self.build_blocks()
        if not self.error:
            self.connect_blocks()
        self.main.full_rebuild_flag = False



    def configure_source(self):
        ##################################################
        # Blocks
        ##################################################
        if self.osmosdr_source == None:
            try:
                self.osmosdr_source = osmosdr.source(args="numchan=" + str(1) + " " + 'rtl=1')
                self.osmosdr_source.set_sample_rate(self.sample_rate)
                self.osmosdr_source.set_center_freq(self.fc, 0)
                self.osmosdr_source.set_freq_corr(self.corr_ppm, 0)
                self.osmosdr_source.set_dc_offset_mode(self.dc_offset_mode, 0)
                self.osmosdr_source.set_iq_balance_mode(self.iq_balance_mode, 0)
                self.osmosdr_source.set_gain_mode(self.gain_mode, 0)
                self.osmosdr_source.set_gain(self.gain, 0)
                self.osmosdr_source.set_if_gain(20, 0)
                self.osmosdr_source.set_bb_gain(20, 0)
                self.osmosdr_source.set_antenna('', 0)
                self.osmosdr_source.set_bandwidth(self.bandwidth, 0)
                self.error = False
            except Exception as e:
                self.error = True
                print('error')

                        

    def limit_offset_range(self, a, b):
        f = abs(a)
        sign = (-1, 1)[a >= 0]
        f = (f, b)[f > b]
        return f * sign

    def ntrp(self, x, xa, xb, ya, yb):
        return (x - xa) * (yb - ya) / (xb - xa) + ya

    def compute_offset_f(self, front_end=True):
        if self.audio_rate != None:
            self.fir_offset_f = self.limit_offset_range(self.fir_offset_f, self.audio_rate / 2)
        if front_end:
            return self.fir_offset_f - self.cw_offset
        else:
            return -(self.fir_offset_f + self.cw_offset)

    def update_freq_xlating_fir_filter(self):
        if self.freq_xlating_fir_filter != None:
            f = self.compute_offset_f(False)
            self.freq_xlating_fir_filter.set_center_freq(f)

    # changing between USB and LSB requires changing the sign of a multiplication term
    def create_usb_lsb_switch(self):
        USB = self.mode == self.main.MODE_USB or self.mode == self.main.MODE_CW_USB
        self.blocks_multiply_const_ssb = blocks.multiply_const_vff(((1, -1)[USB],))

    def create_update_freq_xlating_fir_filter(self):
        if self.sample_rate != None:
            self.fir_offset_f = 0
            if self.mode == self.main.MODE_WFM:
                rate = self.if_sample_rate
            else:
                rate = self.audio_rate

            fir_taps = firdes.complex_band_pass(1, rate, -rate / 2, rate / 2, rate / 2)
            if self.freq_xlating_fir_filter == None:
                self.freq_xlating_fir_filter = filter.freq_xlating_fir_filter_ccc(1, (fir_taps),self.compute_offset_f(False), rate)
            else:
                self.freq_xlating_fir_filter.set_taps(fir_taps)
                self.freq_xlating_fir_filter.set_center_freq(self.compute_offset_f(False))


    def rebuild_filters(self, value):
        if self.cw_base == None:
            return

        am_bw = (8000, 3000, 2000)[value]
        fm_bw = (8000, 6000, 4000)[value]
        wfm_bw = (60e3, 40e3, 20e3)[value]
        ssb_bw = (5000, 2400, 1800)[value]
        cw_bw = (self.cw_base * 2 / 3, self.cw_base / 2, self.cw_base / 3)[value]

        am_taps = firdes.low_pass(
            1, self.audio_rate, am_bw, 500, firdes.WIN_HAMMING, 6.76)
        fm_taps = firdes.low_pass(
            1, self.audio_rate, fm_bw, 500, firdes.WIN_HAMMING, 6.76)
        wfm_taps = firdes.low_pass(
            1, self.if_sample_rate, wfm_bw, 4e3, firdes.WIN_HAMMING, 6.76)
        ssb_taps = firdes.low_pass(
            1, self.audio_rate, ssb_bw, 100, firdes.WIN_HAMMING, 6.76)
        # print("CW Base: %d - %d - %d" % (self.cw_base-cw_bw,self.cw_base + cw_bw,self.audio_rate))
        cw_taps = firdes.band_pass(
            1, self.audio_rate, self.cw_base - cw_bw, self.cw_base + cw_bw, 100, firdes.WIN_HAMMING, 6.76)

        if self.low_pass_filter_am == None:
            self.low_pass_filter_am = filter.fir_filter_ccf(1, am_taps)
        else:
            self.low_pass_filter_am.set_taps(am_taps)

        if self.low_pass_filter_fm == None:
            self.low_pass_filter_fm = filter.fir_filter_ccf(1, fm_taps)
        else:
            self.low_pass_filter_fm.set_taps(fm_taps)

        if self.low_pass_filter_wfm == None:
            self.low_pass_filter_wfm = filter.fir_filter_ccf(1, wfm_taps)
        else:
            self.low_pass_filter_wfm.set_taps(wfm_taps)

        if self.low_pass_filter_ssb == None:
            self.low_pass_filter_ssb = filter.fir_filter_fff(1, ssb_taps)
        else:
            self.low_pass_filter_ssb.set_taps(ssb_taps)

        if self.band_pass_filter_cw == None:
            self.band_pass_filter_cw = filter.fir_filter_fff(1, cw_taps)
        else:
            self.band_pass_filter_cw.set_taps(cw_taps)

    # calculate gcd using Euclid's algorithm
    def gcd(self, a, b):
        while b:
            a, b = b, a % b
        return a

    def compute_dec_interp(self, a, b):
        a = int(a)
        b = int(b)
        gcd = self.gcd(a, b)
        dec = a / gcd
        interp = b / gcd
        return dec, interp

    def compute_offset_f(self, front_end=True):
        if self.audio_rate != None:
            self.fir_offset_f = self.limit_offset_range(self.fir_offset_f, self.audio_rate / 2)
        if front_end:
            return self.fir_offset_f - self.cw_offset
        else:
            return -(self.fir_offset_f + self.cw_offset)

    def test_set_cw_offset(self):
        offset = 0
        if self.mode == self.main.MODE_CW_LSB or self.mode == self.main.MODE_CW_USB:
            if self.mode == self.main.MODE_CW_LSB:
                offset = -self.cw_base / 2
            else:
                offset = self.cw_base / 2
        return offset

    def build_blocks(self):


        ssb_lo = self.ssb_lo
        ssb_hi = self.ssb_hi


        USB = self.mode == 'USB' or self.mode == 'CW_USB'

        self.audio_dec_nrw = 1

        self.dec_nrw, self.interp_nrw = self.compute_dec_interp(self.sample_rate, self.audio_rate)

        self.audio_dec_wid = self.if_sample_rate / self.audio_rate

        self.dec_wid, self.interp_wid = self.compute_dec_interp(self.sample_rate, self.if_sample_rate)

        volume = .1

        self.configure_source()

        self.create_update_freq_xlating_fir_filter()

        self.analog_agc_cc = analog.agc2_cc(1e-1, 1e-2, 1.0, 1.0)
        self.analog_agc_cc.set_max_gain(1)

        self.analog_agc_ff = analog.agc2_ff(1e-1, 1e-2, 1.0, 1.0)
        self.analog_agc_ff.set_max_gain(1)

        self.rational_resampler_wid = filter.rational_resampler_ccc(            
            decimation=int(self.dec_wid),
            interpolation=int(self.interp_wid),            
            taps=None,
            fractional_bw=None,
        )

        self.rational_resampler_nrw = filter.rational_resampler_ccc(
            decimation=int(self.dec_nrw),
            interpolation=int(self.interp_nrw),
            taps=None,
            fractional_bw=None,
        )

        self.analog_pwr_squelch = analog.pwr_squelch_cc(self.squelch_level, 1e-4, 0, True)

        self.analog_pwr_squelch_ssb = analog.pwr_squelch_ff(self.squelch_level, 1e-4, 0, True)

        self.blocks_multiply = blocks.multiply_vcc(1)
        self.blocks_complex_to_real = blocks.complex_to_real(1)

#        self.rebuild_filters()

        self.blocks_complex_to_mag_am = blocks.complex_to_mag(1)

        self.analog_nbfm_rcv = analog.nbfm_rx(
            audio_rate=self.audio_rate,
            quad_rate=self.audio_rate,
            tau=75e-6,
            max_dev=6e3,
        )

        self.analog_wfm_rcv = analog.wfm_rcv(
            quad_rate=self.if_sample_rate,
            audio_decimation=self.audio_dec_wid,
        )

        self.hilbert_fc_2 = filter.hilbert_fc(self.hilbert_taps_ssb, firdes.WIN_HAMMING, 6.76)
        self.hilbert_fc_1 = filter.hilbert_fc(self.hilbert_taps_ssb, firdes.WIN_HAMMING, 6.76)

        self.blocks_multiply_ssb = blocks.multiply_vcc(1)

        self.blocks_complex_to_float_ssb = blocks.complex_to_float(1)

        self.create_usb_lsb_switch()

        self.blocks_add = blocks.add_vff(1)

        self.blocks_complex_to_real = blocks.complex_to_real(1)
        self.blocks_complex_to_imag = blocks.complex_to_imag(1)

        # this is the source for the FFT display's data
        self.logpwrfft = logpwrfft.logpwrfft_c(
            sample_rate = self.sample_rate,
            fft_size = self.fft_size,
            ref_scale = 2,
            frame_rate = self.frame_rate,
            avg_alpha = self.average,
            average = (self.average != 1),
        )

        # this is the main FFT display
        self.fft_vector_sink = MyVectorSink(self.main, self.fft_size)

        self.blocks_multiply_const_volume = blocks.multiply_const_vff((volume,))

        # only create this once
        if self.audio_sink == None:
            try:
                self.audio_sink = audio.sink(self.audio_rate, '', True)
            except Exception as e:
#                self.main.message_dialog("Audio Error",
#                                         "A problem has come up while accessing the audio system: %s" % e)
                self.error = True
                self.audio_sink = None

        self.analog_sig_source_x_0 = analog.sig_source_f(self.sample_rate, analog.GR_COS_WAVE, 1000, 10, 0)

    def connect_blocks(self):
        self.disconnect_all()

        self.cw_offset = self.test_set_cw_offset()
        self.main.set_agc_mode()
        self.rebuild_filters(1)   # 1 is medium

        self.connect((self.osmosdr_source, 0), (self.logpwrfft, 0))
        self.connect((self.logpwrfft, 0), (self.fft_vector_sink, 0))

        if self.mode == self.main.MODE_AM:
            self.connect((self.osmosdr_source, 0), (self.rational_resampler_nrw, 0))
            self.connect((self.rational_resampler_nrw, 0), (self.freq_xlating_fir_filter, 0))
            self.connect((self.freq_xlating_fir_filter, 0), (self.low_pass_filter_am, 0))
            self.connect((self.low_pass_filter_am, 0), (self.analog_pwr_squelch, 0))
            self.connect((self.analog_pwr_squelch, 0), (self.analog_agc_cc, 0))
            self.connect((self.analog_agc_cc, 0), (self.blocks_complex_to_mag_am, 0))
            self.connect((self.blocks_complex_to_mag_am, 0), (self.blocks_multiply_const_volume, 0))
            self.connect((self.blocks_multiply_const_volume, 0), (self.audio_sink, 0))

        elif self.mode == self.main.MODE_FM:
            self.connect((self.osmosdr_source, 0), (self.rational_resampler_nrw, 0))
            self.connect((self.rational_resampler_nrw, 0), (self.freq_xlating_fir_filter, 0))
            self.connect((self.freq_xlating_fir_filter, 0), (self.low_pass_filter_fm, 0))
            self.connect((self.low_pass_filter_fm, 0), (self.analog_pwr_squelch, 0))
            self.connect((self.analog_pwr_squelch, 0), (self.analog_agc_cc, 0))
            self.connect((self.analog_agc_cc, 0), (self.analog_nbfm_rcv, 0))
            self.connect((self.analog_nbfm_rcv, 0), (self.blocks_multiply_const_volume, 0))
            self.connect((self.blocks_multiply_const_volume, 0), (self.audio_sink, 0))

        elif self.mode == self.main.MODE_WFM:
            self.connect((self.osmosdr_source, 0), (self.rational_resampler_wid, 0))
            self.connect((self.rational_resampler_wid, 0), (self.freq_xlating_fir_filter, 0))
            self.connect((self.freq_xlating_fir_filter, 0), (self.low_pass_filter_wfm, 0))
            self.connect((self.low_pass_filter_wfm, 0), (self.analog_pwr_squelch, 0))
            self.connect((self.analog_pwr_squelch, 0), (self.analog_agc_cc, 0))
            self.connect((self.analog_agc_cc, 0), (self.analog_wfm_rcv, 0))
            self.connect((self.analog_wfm_rcv, 0), (self.blocks_multiply_const_volume, 0))
            self.connect((self.blocks_multiply_const_volume, 0), (self.audio_sink, 0))

        elif self.mode == self.main.MODE_USB or self.mode == self.main.MODE_LSB:
            self.create_usb_lsb_switch()
            self.connect((self.osmosdr_source, 0), (self.rational_resampler_nrw, 0))
            self.connect((self.rational_resampler_nrw, 0), (self.freq_xlating_fir_filter, 0))
            self.connect((self.freq_xlating_fir_filter, 0), (self.analog_pwr_squelch, 0))
            self.connect((self.analog_pwr_squelch, 0), (self.blocks_complex_to_float_ssb, 0))
            self.connect((self.blocks_complex_to_float_ssb, 0), (self.hilbert_fc_1, 0))
            self.connect((self.blocks_complex_to_float_ssb, 1), (self.hilbert_fc_2, 0))
            self.connect((self.hilbert_fc_1, 0), (self.blocks_complex_to_real, 0))
            self.connect((self.hilbert_fc_2, 0), (self.blocks_complex_to_imag, 0))
            self.connect((self.blocks_complex_to_imag, 0), (self.blocks_multiply_const_ssb, 0))
            self.connect((self.blocks_multiply_const_ssb, 0), (self.blocks_add, 1))
            self.connect((self.blocks_complex_to_real, 0), (self.blocks_add, 0))
            self.connect((self.blocks_add, 0), (self.low_pass_filter_ssb, 0))
            self.connect((self.low_pass_filter_ssb, 0), (self.analog_pwr_squelch_ssb, 0))
            self.connect((self.analog_pwr_squelch_ssb, 0), (self.analog_agc_ff, 0))
            self.connect((self.analog_agc_ff, 0), (self.blocks_multiply_const_volume, 0))
            self.connect((self.blocks_multiply_const_volume, 0), (self.audio_sink, 0))

        elif self.mode == self.main.MODE_CW_USB or self.mode == self.main.MODE_CW_LSB:
            self.create_usb_lsb_switch()
            self.connect((self.osmosdr_source, 0), (self.rational_resampler_nrw, 0))
            self.connect((self.rational_resampler_nrw, 0), (self.freq_xlating_fir_filter, 0))
            self.connect((self.freq_xlating_fir_filter, 0), (self.analog_pwr_squelch, 0))
            self.connect((self.analog_pwr_squelch, 0), (self.blocks_complex_to_float_ssb, 0))
            self.connect((self.blocks_complex_to_float_ssb, 0), (self.hilbert_fc_1, 0))
            self.connect((self.blocks_complex_to_float_ssb, 1), (self.hilbert_fc_2, 0))
            self.connect((self.hilbert_fc_1, 0), (self.blocks_complex_to_real, 0))
            self.connect((self.hilbert_fc_2, 0), (self.blocks_complex_to_imag, 0))
            self.connect((self.blocks_complex_to_imag, 0), (self.blocks_multiply_const_ssb, 0))
            self.connect((self.blocks_multiply_const_ssb, 0), (self.blocks_add, 1))
            self.connect((self.blocks_complex_to_real, 0), (self.blocks_add, 0))
            self.connect((self.blocks_add, 0), (self.band_pass_filter_cw, 0))
            self.connect((self.band_pass_filter_cw, 0), (self.analog_pwr_squelch_ssb, 0))
            self.connect((self.analog_pwr_squelch_ssb, 0), (self.analog_agc_ff, 0))
            self.connect((self.analog_agc_ff, 0), (self.blocks_multiply_const_volume, 0))

            self.connect((self.blocks_multiply_const_volume, 0), (self.audio_sink, 0))

        else:
            print("mode error -- no recognizable mode selected.")










