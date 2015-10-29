#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import sys
import os
import logging
import datetime
import numpy as np
from PyQt4 import QtGui, QtCore, uic
from utils import limit


from arduino import SensorsArduino
from utils import linear_function_with_limit

import pyqtgraph as pg

logger = logging.getLogger(__name__)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, analog_input, *args, **kwargs):
        self.ai = analog_input
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui",
            "calibrate.ui"), self)

        self.cal_plot = pg.PlotWidget()
        self.gridLayout.addWidget(self.cal_plot)

        self.plot_calibrate_func()

    def plot_calibrate_func(self):
        pen = pg.mkPen('r', style=QtCore.Qt.SolidLine)
        N = 2**self.ai.bits_resolution  # ADC resolution = 10 bits = 2**10 = 1024
        self.cal_plot.plot(np.arange(1024), [self.ai._calibrate_func(i) for i in range(N)], pen=pen)
        #self.dot_plot.plot()

    def update(self): #, sensors):
        logger.info("update MainWindow with %s" % self.ai)
        self.progressBar.setValue(self.ai.value)
        self.lblRawValue.setText("%.1f" % self.ai.raw)
        self.lblValue.setText("%.1f" % self.ai.value)
        pen = pg.mkPen('g', style=QtCore.Qt.SolidLine)

        #self.dot_plot.plot(self.ai.raw, self.ai.value)
        #self.cal_plot.plot((0, float(self.ai.raw)), (0, self.ai.value), pen=pen, symbol='+')
        
        #print(self.cal_curve.__dict__)
        #self.cal_curve.plot(np.arange(1024), np.arange(1024)*2+1)


class MyApplication(QtGui.QApplication):
    def __init__(self, *args, **kwargs):
        device = kwargs.pop('device')
        baudrate = kwargs.pop('baudrate')
        super(MyApplication, self).__init__(*args, **kwargs)

        self.t = datetime.datetime.utcnow()
        self.t_last = self.t

        #self.sensors = 50.0
        self.sensors00 = SensorsArduino(device=device, baudrate=baudrate, adc_channels_number=2, read_error_exception=False)
        self.sensors00.connect()
        ai = self.sensors00.ADC[0]
        ai.calibrate(lambda value: linear_function_with_limit(value, 520.0, 603.0, 0.0, 100.0))
        #ai.calibrate(lambda value: linear_function_with_limit(value, 0.0, 2**ai.bits_resolution - 1, 0.0, 100.0))
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        period_disp_ms = 50
        logging.info("period_disp_ms: %f" % period_disp_ms)
        self.timer.start(period_disp_ms)

        self.mainWin = MainWindow(ai)
        self.mainWin.show()

    def update(self):
        self.t = datetime.datetime.utcnow()

        #self.sensors = limit(self.sensors + np.random.uniform(-5, 5), 0.0, 100.0)

        if self.sensors00.read():
            logger.info("update %s %s %s %s" % (self.t, self.t_last, self.t - self.t_last, self.sensors00.ADC[0]))
            self.mainWin.update() #self.sensors00)
            
            self.t_last = self.t

@click.command()
@click.option('--device', default='/dev/ttyUSB0', help='device')
@click.option('--baudrate', default=57600, help='Baudrate (9600 14400 19200 28800 38400 57600 115200) - default to 57600')
def main(device, baudrate):
    logging.basicConfig(level=logging.INFO)
    app = MyApplication(sys.argv, device=device, baudrate=baudrate)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
