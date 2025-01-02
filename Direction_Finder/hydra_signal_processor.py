# KerberosSDR Signal Processor
#
# Copyright (C) 2018-2019  Carl Laufer, Tamás Pető
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# -*
# - coding: utf-8 -*-

import sys
import os
import time
# Math support
import numpy as np

# Signal processing support
from scipy import fft,ifft
from scipy import signal
from scipy.signal import correlate

# Plot support
#import matplotlib.pyplot as plt

# GUI support
from PyQt5 import QtCore

# Import the pyArgus module
#root_path = os.getcwd()
#pyargus_path = os.path.join(os.path.join(root_path, "pyArgus"), "pyArgus")
#sys.path.insert(0, pyargus_path)
#import directionEstimation_v1p15 as de

from pyargus import directionEstimation as de


# Import APRiL module
#april_path = os.path.join(os.path.join(root_path, "_APRIL"), "APRIL")
#sys.path.insert(0, april_path)
#import channelPreparation as cp
#import clutterCancellation as cc
#import detector as det



class SignalProcessor(QtCore.QThread):
    
    signal_DOA_ready = QtCore.pyqtSignal()
    signal_sync_ready = QtCore.pyqtSignal()
    signal_progressbar = QtCore.pyqtSignal(int)


    def __init__(self, parent=None, module_receiver=None):
        """
            Description:
            ------------

            Parameters:
            -----------

            Return values:
            --------------

        """
        super(SignalProcessor, self).__init__(parent)

        self.module_receiver = module_receiver
        self.en_spectrum = False
        self.en_record = False
        self.en_sample_offset_sync = False
        self.en_calib_DOA_90 =False
        self.en_sync = False
        self.en_calib_iq = False
        self.en_DOA_estimation = False
        self.en_noise_source = False

         # DOA processing options
        self.en_DOA_Bartlett = False
        self.en_DOA_Capon = False
        self.en_DOA_MEM = False
        self.en_DOA_MUSIC = True
        self.en_DOA_FB_avg = False
        self.DOA_inter_elem_space = 0.45
        self.DOA_ant_alignment = "UCA"
        
        self.center_freq = 0  # TODO: Initialize this [Hz]
        self.fs = 1.024 * 10**6  # Decimated sampling frequncy - Update from GUI
        self.channel_number = 4   

        # Processing parameters        
        self.test = None
        self.spectrum_sample_size = 2**14 #2**14
        self.DOA_sample_size = 2**15 # Connect to GUI value??
        self.xcorr_sample_size = 2**18 #2**18
        self.spectrum = np.ones((self.channel_number+1,self.spectrum_sample_size), dtype=np.float32)
        self.xcorr = np.ones((self.channel_number-1,self.xcorr_sample_size*2), dtype=np.complex64)        
        self.phasor_win = 2**10 # Phasor plot window
        self.phasors = np.ones((self.channel_number-1, self.phasor_win), dtype=np.complex64)
        self.run_processing = False
        
        # Result vectors
        self.delay_log = np.array([[0], [0], [0]])
        self.phase_log = np.array([[0], [0], [0]])
        self.DOA_Bartlett_res = np.ones(181)
        self.DOA_Capon_res = np.ones(181)
        self.DOA_MEM_res = np.ones(181)
        self.DOA_MUSIC_res = np.ones(181)
        self.DOA_theta = np.arange(0,181,1)
        
        
        # Auto resync params
        self.lastTime = 0
        self.runningSync = 0
        self.timed_sync = False
        self.resync_time = -1

    def run(self):
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        #    
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        self.run_processing = True
        
        while self.run_processing:
            start_time = time.time()

            # Download samples
            # if(self.en_sync or self.en_spectrum):
            time.sleep(0.25)  # You can play with this value, but it may affect stability

            self.module_receiver.download_iq_samples()

            self.DOA_sample_size = self.module_receiver.iq_samples[0, :].size
            self.xcorr_sample_size = self.module_receiver.iq_samples[0,:].size
            self.xcorr = np.ones((self.channel_number-1,self.xcorr_sample_size*2), dtype=np.complex64)           

            # Synchronization
            if self.en_sync :
                # print("Sync graph enabled")
                self.sample_delay()
                self.signal_sync_ready.emit()

            # Sample offset compensation request
            if self.en_sample_offset_sync:
                self.module_receiver.set_sample_offsets(self.delay_log[:, -1])
                self.en_sample_offset_sync = False

            # IQ calibration request
            if self.en_calib_iq:
                # IQ correction
                for m in range(self.channel_number):
                    self.module_receiver.iq_corrections[m] *= np.size(self.module_receiver.iq_samples[0, :]) / (
                        np.dot(self.module_receiver.iq_samples[m, :], self.module_receiver.iq_samples[0, :].conj()))
                c = np.sqrt(np.sum(np.abs(self.module_receiver.iq_corrections) ** 2))
                self.module_receiver.iq_corrections = np.divide(self.module_receiver.iq_corrections, c)
                # print("Corrections: ",self.module_receiver.iq_corrections)
                self.en_calib_iq = False


            if self.en_DOA_estimation:
                # Get FFT for squelch
                self.spectrum[1, :] = 10 * np.log10(np.fft.fftshift(np.abs(np.fft.fft(self.module_receiver.iq_samples[0, 0: self.spectrum_sample_size]))))
                self.estimate_DOA()
                self.signal_DOA_ready.emit()


            if self.en_record:
                np.save('hydra_samples.npy', self.module_receiver.iq_samples)

    def iq_calibration(self):
        #IQ correction
        for m in range(self.channel_number):
            self.module_receiver.iq_corrections[m] *= np.size(self.module_receiver.iq_samples[0, :]) / (
                np.dot(self.module_receiver.iq_samples[m, :], self.module_receiver.iq_samples[0, :].conj()))
        c = np.sqrt(np.sum(np.abs(self.module_receiver.iq_corrections) ** 2))
        self.module_receiver.iq_corrections = np.divide(self.module_receiver.iq_corrections, c)


    def sample_delay(self):
         #print("Entered sample delay func")
        N = self.xcorr_sample_size
        iq_samples = self.module_receiver.iq_samples[:, 0:N]
       
        delays = np.array([[0],[0],[0]])
        phases = np.array([[0],[0],[0]])
        # Channel matching
        np_zeros = np.zeros(N, dtype=np.complex64)
        x_padd = np.concatenate([iq_samples[0, :], np_zeros])
        x_fft = np.fft.fft(x_padd)
        for m in np.arange(1, self.channel_number):
            y_padd = np.concatenate([np_zeros, iq_samples[m, :]])
            y_fft = np.fft.fft(y_padd)            
            self.xcorr[m-1] = np.fft.ifft(x_fft.conj() * y_fft)
            delay = np.argmax(np.abs(self.xcorr[m-1])) - N
            #phase = np.rad2deg(np.angle(self.xcorr[m-1, delay + N]))
            phase = np.rad2deg(np.angle(self.xcorr[m-1, N]))
            
            #offset = 50000                     
            #self.phasors[m-1, :] = (iq_samples[0, offset: self.phasor_win+offset] * iq_samples[m, offset+delay: self.phasor_win+offset+delay].conj())
            #self.phasors[m-1, :] = (iq_samples[0, 0: self.phasor_win] * iq_samples[m, 0: self.phasor_win].conj())
            
            """
            self.IQSamples[1, :] = np.roll(self.IQSamples[1, :], delay * -1)
            if delay > 0:
                self.IQSamples[1, -delay::] = np.zeros(delay, dtype=np.complex64)
            if delay < 0:
                self.IQSamples[1, 0: np.abs(delay)] = np.zeros(np.abs(delay), dtype=np.complex64)
            """
            #msg = "[ INFO ] delay: " + str(delay)
            #print(msg)
            delays[m-1,0] = delay
            phases[m-1,0] = phase

        self.delay_log = np.concatenate((self.delay_log, delays),axis=1)
        self.phase_log = np.concatenate((self.phase_log, phases),axis=1)

    def delete_sync_history(self):
        self.delay_log = np.array([[0], [0], [0]])
        self.phase_log = np.array([[0], [0], [0]])

    def estimate_DOA(self):
        #print("[ INFO ] Python DSP: Estimating DOA")

        iq_samples = self.module_receiver.iq_samples[:, 0:self.DOA_sample_size]
        # Calculating spatial correlation matrix
        R = de.corr_matrix_estimate(iq_samples.T, imp="fast")

        if self.en_DOA_FB_avg:
            R=de.forward_backward_avg(R)

        M = np.size(iq_samples, 0)

        self.DOA_theta =  np.linspace(0,360,361)
            #scanning_vectors = de.gen_uca_scanning_vectors(M, self.DOA_inter_elem_space, self.DOA_theta)
        x = self.DOA_inter_elem_space * np.cos(2*np.pi/M * np.arange(M))
        y = self.DOA_inter_elem_space * np.sin(-2*np.pi/M * np.arange(M)) # For this specific array only
        scanning_vectors = de.gen_scanning_vectors(M, x, y, self.DOA_theta)

        self.DOA_MUSIC_res = de.DOA_MUSIC(R, scanning_vectors, signal_dimension = 1)               

        
         #print(self.DOA_MUSIC_res)


    def stop(self):
        self.run_processing = False


def busy_wait(dt):
    current_time = time.time()
    while (time.time() < current_time+dt):
        pass
