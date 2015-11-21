#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

import os
import pandas as pd

import matplotlib.pyplot as plt

COL_T = 't'

@click.command()
@click.argument('directory')
@click.option('--max_rows', default=20, help='Pandas display.max_rows')
@click.option('--plot', default='', help='Plot (frame, position...)')
def main(directory, max_rows, plot):
    directory = os.path.expanduser(directory)
    filename = os.path.join(directory, 'data.csv')
    print("Reading %r" % filename)
    pd.set_option('display.max_rows', max_rows)

    df = pd.read_csv(filename)
    df[COL_T] = pd.to_datetime(df[COL_T])
    df = df.set_index(COL_T)
    print(df)

    if plot == '':
        plot = df.columns
    else:
        plot = plot.split(',')

    ax = df[plot].plot(style='-+')
    plt.show()

if __name__ == '__main__':
    main()
