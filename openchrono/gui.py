#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import sys
import os
import logging
from PyQt4 import QtGui, QtCore, uic

logger = logging.getLogger(__name__)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),
            "gui.ui"), self)

class MyApplication(QtGui.QApplication):
    def __init__(self, *args, **kwargs):
        device = kwargs.pop('device')
        baudrate = kwargs.pop('baudrate')
        super(MyApplication, self).__init__(*args, **kwargs)
        self.mainWin = MainWindow()
        self.mainWin.show()

@click.command()
@click.option('--device', default='/dev/ttyUSB0', help='device')
@click.option('--baudrate', default=57600, help='Baudrate')
def main(device, baudrate):
    app = MyApplication(sys.argv, device=device, baudrate=baudrate)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
