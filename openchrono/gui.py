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

logger = logging.getLogger(__name__)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),
            "gui.ui"), self)

    def update(self, sensors):
        logger.info("update MainWindow with %s" % sensors)
        ai0 = sensors.ADC[0]
        self.progressBar.setValue(ai0.value)
        self.lblRawValue.setText("%.1f" % ai0.raw)
        self.lblValue.setText("%.1f" % ai0.value)


class MyApplication(QtGui.QApplication):
    def __init__(self, *args, **kwargs):
        device = kwargs.pop('device')
        baudrate = kwargs.pop('baudrate')
        super(MyApplication, self).__init__(*args, **kwargs)

        self.t = datetime.datetime.utcnow()
        self.t_last = self.t

        #self.sensors = 50.0
        self.sensors00 = SensorsArduino(device=device, baudrate=baudrate, adc_channels_number=2, read_error_exception=True)
        self.sensors00.connect()
        self.sensors00.ADC[0].calibrate(lambda value: linear_function_with_limit(value, 520.0, 603.0, 0.0, 100.0))

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        period_disp_ms = 50
        logging.info("period_disp_ms: %f" % period_disp_ms)
        self.timer.start(period_disp_ms)

        self.mainWin = MainWindow()
        self.mainWin.show()

    def update(self):
        self.t = datetime.datetime.utcnow()

        #self.sensors = limit(self.sensors + np.random.uniform(-5, 5), 0.0, 100.0)

        if self.sensors00.read():
            logger.info("update %s %s %s %s" % (self.t, self.t_last, self.t - self.t_last, self.sensors00.ADC[0]))
            self.mainWin.update(self.sensors00)
            
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
