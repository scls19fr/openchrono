#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        super(MyApplication, self).__init__(*args, **kwargs)
        self.mainWin = MainWindow()
        self.mainWin.show()

def main():
    app = MyApplication(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
