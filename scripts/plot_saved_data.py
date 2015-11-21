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
@click.option('--plots', default='', help='Plot (frame, position...)')
@click.option('--stacked/--no-stacked', default=True, help='Stacked plot')
def main(directory, max_rows, plots, stacked):
    directory = os.path.expanduser(directory)
    filename = os.path.join(directory, 'data.csv')
    print("Reading %r" % filename)
    pd.set_option('display.max_rows', max_rows)

    df = pd.read_csv(filename)
    df[COL_T] = pd.to_datetime(df[COL_T])
    df = df.set_index(COL_T)
    print(df)

    if plots == '':
        plots = df.columns
    else:
        plots = plots.split(',')

    if stacked:
        fig, axs = plt.subplots(nrows=len(plots))
    
        for i, plot in enumerate(plots):
            ax = axs[i]
            ax.plot(df.index, df[plot])
            ax.set_xlabel(COL_T) #, fontdict=font)
            ax.set_ylabel(plot)
            #ax.set_title(plot)
    else:
        ax = df[plots].plot(style='-+')

    plt.show()

if __name__ == '__main__':
    main()
