#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

COL_T = 't'
COL_FRAME = 'frame'

from openchrono.filename import FilenameFactory


def postprocessing(df, col_t=COL_T, index='frame'):
    df[COL_T] = pd.to_datetime(df[COL_T])
    sensors = df.columns.drop([COL_T, COL_FRAME]) # every columns except 't' and 'frame' (sensors)

    if index in ['frame', 'f']:
        s_null_t = df[COL_T].isnull()
        df[COL_T] = df[COL_T].astype(np.int64)
        frame_min = df['frame'].min()
        frame_max = df['frame'].max()
        df_grp = df.groupby('frame').mean()
        df_grp['measures'] = True
        idx = pd.Index(np.arange(frame_min, frame_max + 1), name='frame')
        df = pd.DataFrame(columns = df_grp.columns, index=idx)
        df.loc[df_grp.index, :] = df_grp

        # interpolate NaT values in 't' column with a linear regression
        #df[COL_T] = df[COL_T].fillna(method='ffill')
        # ToDo:
        # http://stackoverflow.com/questions/33921795/fill-timestamp-nat-with-a-linear-interpolation/33922824?noredirect=1#comment55606782_33922824
        # https://github.com/pydata/pandas/issues/11701
        df[COL_T] = df[COL_T].astype(np.float64)
        df.loc[s_null_t, COL_T] = np.nan
        df[COL_T] = df[COL_T].interpolate()
        df[COL_T] = pd.to_datetime(df[COL_T] / 1000, unit='us')

        df['measures'] = df['measures'].fillna(False)
        df[sensors] = df[sensors].fillna(method='ffill')

    elif index in ['time', 't']:
        pass

    else:
        raise NotImplementedError("%r not supported" % index)

    df['td'] = df[COL_T] - df[COL_T].shift(1)
    td_unit = np.timedelta64(1, 's')
    df['td'] = df['td'].map(lambda x: x / td_unit)
    df['t0'] = df[COL_T].map(lambda x: x - df[COL_T][0])
    df['t0'] = df['t0'].map(lambda x: x / td_unit)
    if index in ['time', 't']:
        df = df.set_index(COL_T)
    return df, sensors

@click.command()
@click.argument('directory')
@click.option('--max-rows', default=20, help='Pandas display.max_rows')
@click.option('--filename-out', default='data_postprocessed.csv', help='Filename output')
@click.option('--index', default='frame', help="Set index to 'time' or to 'frame'")
def main(directory, max_rows, filename_out, index):
    filename = FilenameFactory(directory)
    filename_in = filename.data
    index = index.lower()
    print("Reading %r" % filename_in)
    pd.set_option('display.max_rows', max_rows)

    df = pd.read_csv(filename_in)
    df, sensors = postprocessing(df, COL_T, index)

    print(df)
    filename_out = filename.create(filename_out)
    df.to_csv(filename_out)


if __name__ == '__main__':
    main()
