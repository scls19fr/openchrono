#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

import sys
import os
import logging

import datetime

import numpy as np
import pandas as pd

from PyQt4 import QtGui, QtCore, uic

import pyqtgraph as pg
from data_postprocessing import (get_data_filename, 
        get_video_filename, postprocessing)

logger = logging.getLogger(__name__)


class DisplayVideoMainWindow(QtGui.QMainWindow):
    def __init__(self, directory, *args, **kwargs):
        self.directory = directory
        super(DisplayVideoMainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui",
            "display_video.ui"), self)

        self.cal_plot = pg.PlotWidget()
        self.setWindowTitle(self.directory);
        self.data_filename = get_data_filename(directory)
        self.video_filename = get_video_filename(directory)

        logger.info("Reading %r" % self.data_filename)
        self.df = pd.read_csv(self.data_filename)
        self.df, self.sensors = postprocessing(self.df, 't', 'frame')
        frame_min, frame_max = self.df.index.min(), self.df.index.max()
        
        self.horizontalSlider.setMinimum(frame_min)
        self.horizontalSlider.setMaximum(frame_max)
        self.horizontalSlider.valueChanged.connect(self.slider_changed)

        print(self.df)

    def slider_changed(self, frame):
        print("go to frame %d" % frame)

    def update(self, *args, **kwargs):
        print("update")


class DisplayVideoApp(QtGui.QApplication):
    def __init__(self, *args, **kwargs):
        directory = kwargs.pop('directory')
        super(DisplayVideoApp, self).__init__(*args, **kwargs)

        self.mainWin = DisplayVideoMainWindow(directory)
        self.mainWin.show()

    def update(self):
        pass

@click.command()
@click.argument('directory')
def main(directory):
    logging.basicConfig(level=logging.INFO)

    # Set PyQtGraph colors
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')

    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)
  

    app = DisplayVideoApp(sys.argv, directory=directory)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
