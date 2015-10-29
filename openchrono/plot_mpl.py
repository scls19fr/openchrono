#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import time
import matplotlib.pyplot as plt
import numpy as np
import datetime
import logging
import traceback
from numpy_buffer import RingBuffer

from arduino import SensorsArduino
from utils import linear_function_with_limit


logger = logging.getLogger(__name__)


@click.command()
@click.option('--device', default='/dev/ttyUSB0', help='device')
@click.option('--baudrate', default=57600, help='Baudrate (9600 14400 19200 28800 38400 57600 115200) - default to 57600')
def main(device, baudrate):
    logging.basicConfig(level=logging.INFO)
    
    sensors00 = SensorsArduino(device=device, baudrate=baudrate, adc_channels_number=2)
    print("capabilities: %s" % sensors00.capabilities)
    sensors00.connect()
    sensors00.ADC[0].calibrate(lambda value: linear_function_with_limit(value, 520.0, 603.0, 0.0, 100.0))
        
    maxlen = 100
    data_x = RingBuffer(maxlen, datetime.datetime.utcnow(), dtype=datetime.datetime)
    data_y = RingBuffer(maxlen)

    y = 100 # initial value

    fig, ax = plt.subplots()
    line, = ax.plot(data_x.all[::-1], data_y.all[::-1], linestyle='-', marker='+', color='r', markeredgecolor='b')
    #ax.set_ylim([0, 1023])
    ax.set_ylim([0, 100])

    t_last = datetime.datetime.utcnow()
    while True:
        t = datetime.datetime.utcnow()
        try:
            if sensors00.read() and sensors00.ADC[0].has_new_data:
                print(sensors00._bin_msg._data)
                y = sensors00.ADC[0].value
                #y = limit(y, 1800.0, 24000.0, 0.0, 100.0)
                logger.info("%s %s %s" % (t, y, t - t_last))
                data_x.append(t)
                data_y.append(y)
                line.set_xdata(data_x.all[::-1])
                xmin, xmax = data_x.min(), data_x.max()
                if xmax > xmin:
                    ax.set_xlim([xmin, xmax])
                    line.set_ydata(data_y.all[::-1])
                    #ymin, ymax = data_y.min(), data_y.max()
                    #if ymax > ymin:
                    #    ax.set_ylim([ymin, ymax])
                plt.pause(0.001)
        except Exception as e:
            logger.error(traceback.format_exc())
            #raise e
        t_last = t

if __name__ == '__main__':
    main()
