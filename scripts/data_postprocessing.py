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
@click.option('--index', default='time', help="Set index to 'time' or to 'frame'")
def main(directory, max_rows, filename_out, index):
    directory = os.path.expanduser(directory)
    filename_in = os.path.join(directory, 'data.csv')
    index = index.lower()
    print("Reading %r" % filename_in)
    pd.set_option('display.max_rows', max_rows)

    df = pd.read_csv(filename_in)
    df[COL_T] = pd.to_datetime(df[COL_T])
    if index == 'time':
        df = df.set_index(COL_T)
    elif index == 'frame':
        df[COL_T] = df[COL_T].astype(np.int64)
        frame_min = df['frame'].min()
        frame_max = df['frame'].max()
        df_grp = df.groupby('frame').mean()
        df_grp['measures'] = True
        idx = pd.Index(np.arange(frame_min, frame_max + 1), name='frame')
        df = pd.DataFrame(columns = df_grp.columns, index=idx)
        df.loc[df_grp.index, :] = df_grp
        df[COL_T] = df[COL_T].fillna(method='ffill') # ToDo: use a linear regression instead
        df[COL_T] = pd.to_datetime(df[COL_T] / 1000, unit='us')
        df['measures'] = df['measures'].fillna(False)
        sensors = df.columns[1:] # every columns except 't' (sensors)
        df[sensors] = df[sensors].fillna(method='ffill')

    df['td'] = df[COL_T] - df[COL_T].shift(1)
    td_unit = np.timedelta64(1, 's')
    df['td'] = df['td'].map(lambda x: x / td_unit)
    df['t0'] = df[COL_T].map(lambda x: x - df[COL_T][0])
    df['t0'] = df['t0'].map(lambda x: x / td_unit)
    print(df)
    filename_out = os.path.join(directory, filename_out)
    df.to_csv(filename_out)


if __name__ == '__main__':
    main()
