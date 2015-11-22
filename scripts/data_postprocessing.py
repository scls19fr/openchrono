#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

COL_T = 't'

@click.command()
@click.argument('directory')
@click.option('--max-rows', default=20, help='Pandas display.max_rows')
@click.option('--filename-out', default='data_postprocessed.csv', help='Filename output')
def main(directory, max_rows, filename_out):
    directory = os.path.expanduser(directory)
    filename_in = os.path.join(directory, 'data.csv')
    print("Reading %r" % filename_in)
    pd.set_option('display.max_rows', max_rows)

    df = pd.read_csv(filename_in)
    df[COL_T] = pd.to_datetime(df[COL_T])
    df['td'] = df[COL_T] - df[COL_T].shift(1)
    td_unit = np.timedelta64(1, 's')
    df['td'] = df['td'].map(lambda x: x / td_unit)
    df = df.set_index(COL_T)
    df['t0'] = df.index.map(lambda x: x - df.index[0])
    df['t0'] = df['t0'].map(lambda x: x / td_unit)
    print(df)
    filename_out = os.path.join(directory, filename_out)
    df.to_csv(filename_out)


if __name__ == '__main__':
    main()
