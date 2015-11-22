#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from collections import namedtuple

COL_T = 't'

class VideoOverlay(object):
    def __init__(self, directory):
        self.directory = directory

        self.filename_data_in = os.path.join(directory, 'data.csv')
        self.filename_video_in = os.path.join(directory, 'video.h264')
        self.filename_video_out = os.path.join(directory, 'video_overlay.h264')
        
        self.directory_images = os.path.join(directory, 'images')
                
    
    @property
    def records(self):
        print("Reading %r" % self.filename_data_in)

        df = pd.read_csv(self.filename_data_in)
        df[COL_T] = pd.to_datetime(df[COL_T])
        df = df.set_index(COL_T)
        columns = tuple([COL_T] + list(df.columns))
        Record = namedtuple('Record', columns)
        for dat in df.itertuples():
            record = Record(*dat)
            yield(record)
            
    def create_images(self):
        pass
    
    def create_overlay_video(self):
        pass

@click.command()
@click.argument('directory')
@click.option('--max_rows', default=20, help='Pandas display.max_rows')
def main(directory, max_rows):
    pd.set_option('display.max_rows', max_rows)

    directory = os.path.expanduser(directory)

    overlay = VideoOverlay(directory)
    for record in overlay.records:
        print(record)
    
if __name__ == '__main__':
    main()
