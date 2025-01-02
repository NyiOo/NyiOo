import os,threading
import subprocess, pprint, shlex
import numpy as np

from PyQt5.QtCore import QThread , pyqtSignal ,QSettings

class Info:
    """Default device metadata"""
    sample_rate_min = 0
    sample_rate_max = 3200000
    sample_rate = 2560000
    bandwidth_min = 0
    bandwidth_max = 0
    bandwidth = 0
    gain_min = -1
    gain_max = 49
    gain = 37
    start_freq_min = 24
    start_freq_max = 2200
    start_freq = 87
    stop_freq_min = 24
    stop_freq_max = 2200
    stop_freq = 108
    bin_size_min = 0
    bin_size_max = 2800
    bin_size = 10
    interval_min = 0
    interval_max = 999
    interval = 10
    ppm_min = -999
    ppm_max = 999
    ppm = 0
    crop_min = 0
    crop_max = 99
    crop = 0
    additional_params = ''
    help_device = None

    @classmethod
    def help_params(cls, executable):
        try:
            p = subprocess.run([executable, '-h'], universal_newlines=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               env=dict(os.environ, COLUMNS='125'))
            text = p.stdout
        except OSError:
            text = '{} executable not found!'.format(executable)
        return text

class PowerThread(QThread):
    """Thread which runs Power Spectral Density acquisition and calculation process"""
    powerThreadStarted = pyqtSignal()
    powerThreadStopped = pyqtSignal()

    def __init__(self, data_storage, parent=None):
        super().__init__(parent)
        self.data_storage = data_storage
        self.alive = False
        self.process = None
        self._shutdown_lock = threading.Lock()

    def stop(self):
        """Stop power process thread"""
        self.process_stop()
        self.alive = False
        self.wait()

    def setup(self, start_freq, stop_freq, bin_size, interval=10.0, gain=-1, ppm=0, crop=0,
              single_shot=False, device=0, sample_rate=2560000, bandwidth=0, lnb_lo=0):
        """Setup rtl_power params"""
        if bin_size > 2800:
            bin_size = 2800
        self.params = {
            "start_freq": start_freq,
            "stop_freq": stop_freq,
            "bin_size": bin_size,
            "interval": interval,
            "device": device,
            "hops": 0,
            "gain": gain,
            "ppm": ppm,
            "crop": crop,
            "single_shot": single_shot
        }
        self.lnb_lo = lnb_lo
        self.databuffer = {}
        self.last_timestamp = ""

        print("rtl_power params:")
        pprint.pprint(self.params)
        print()

    def process_start(self):
        """Start rtl_power process"""
        if not self.process and self.params:
            settings = QSettings()
            cmdline = shlex.split("rtl_power")
            cmdline.extend([
                "-f", "{}M:{}M:{}k".format(self.params["start_freq"] - self.lnb_lo / 1e6,
                                           self.params["stop_freq"] - self.lnb_lo / 1e6,
                                           self.params["bin_size"]),
                "-i", "{}".format(self.params["interval"]),
                "-d", "{}".format(self.params["device"]),
                "-p", "{}".format(self.params["ppm"]),
                "-c", "{}".format(self.params["crop"])
            ])

            if self.params["gain"] >= 0:
                cmdline.extend(["-g", "{}".format(self.params["gain"])])
            if self.params["single_shot"]:
                cmdline.append("-1")

            additional_params = settings.value("params", Info.additional_params)
            if additional_params:
                cmdline.extend(shlex.split(additional_params))

            self.process = subprocess.Popen(cmdline, stdout=subprocess.PIPE,universal_newlines=True)

    def process_stop(self):
        """Terminate power process"""
        with self._shutdown_lock:
            if self.process:
                try:
                    self.process.terminate()
                except ProcessLookupError:
                    pass
                self.process.wait()
                self.process = None

    def parse_output(self, line):
        """Parse one line of output from rtl_power"""
        line = [col.strip() for col in line.split(",")]
        timestamp = " ".join(line[:2])
        start_freq = int(line[2])
        stop_freq = int(line[3])
        step = float(line[4])
        samples = float(line[5])

        x_axis = list(np.arange(start_freq + self.lnb_lo, stop_freq + self.lnb_lo, step))
        y_axis = [float(y) for y in line[6:]]
        if len(x_axis) != len(y_axis):
            print("ERROR: len(x_axis) != len(y_axis), use newer version of rtl_power!")
            if len(x_axis) > len(y_axis):
                print("Trimming x_axis...")
                x_axis = x_axis[:len(y_axis)]
            else:
                print("Trimming y_axis...")
                y_axis = y_axis[:len(x_axis)]

        if timestamp != self.last_timestamp:
            self.last_timestamp = timestamp
            self.databuffer = {"timestamp": timestamp,
                               "x": x_axis,
                               "y": y_axis}
        else:
            self.databuffer["x"].extend(x_axis)
            self.databuffer["y"].extend(y_axis)

        # This have to be stupid like this to be compatible with old broken version of rtl_power. Right way is:
        # if stop_freq == (self.params["stop_freq"] - self.lnb_lo / 1e6) * 1e6:
        if stop_freq > ((self.params["stop_freq"] - self.lnb_lo / 1e6) * 1e6) - step:
            self.data_storage.update(self.databuffer)

    def run(self):
        """Power process thread main loop"""
        self.process_start()
        self.alive = True
        self.powerThreadStarted.emit()


        for line in self.process.stdout:
            if not self.alive:
                break
            self.parse_output(line)

        self.process_stop()

        self.alive = False
        self.powerThreadStopped.emit()