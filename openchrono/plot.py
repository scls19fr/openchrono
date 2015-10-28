#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import time
import serial
import struct
import matplotlib.pyplot as plt
import numpy as np
import datetime
import logging
from numpy_buffer import RingBuffer

from arduino import ArduinoBinaryMessage
from utils import limit

#def read_sensors():
#    pass

logger = logging.getLogger(__name__)


@click.command()
@click.option('--device', default='/dev/ttyUSB0', help='device')
@click.option('--baudrate', default=57600, help='Baudrate (9600 14400 19200 28800 38400 57600 115200) - default to 57600')
def main(device, baudrate):
    #port = '/dev/ttyUSB0'
    #baudrate = 57600 # 9600 14400 19200 28800 38400 57600 115200
    ser = serial.Serial(device, baudrate)
    ardu_bin_msg = ArduinoBinaryMessage(adc_channels_number=2)

    #sensors00 = Arduino()
    #sensors00.connect(device=device, baudrate=baudrate, adc_channels_number=2)
    #sensors00.read()

    # reset the arduino
    ser.setDTR(level=False)
    time.sleep(0.5)
    # ensure there is no stale data in the buffer
    ser.flushInput()
    ser.setDTR()
    time.sleep(0.5)

    print("waiting for arduino...")

    # initial handshake w/ arduino
    allowed_byte = 0x07
    while True:
        byte_received = struct.unpack("B", ser.read())[0]
        print("handshake: %s" % byte_received)
        if byte_received == allowed_byte:
            break
    ser.flushInput()
    ser.write(b'\x10')

    print("connected to arduino...")
    
    
    maxlen = 100
    data_x = RingBuffer(maxlen, datetime.datetime.utcnow(), dtype=datetime.datetime)
    data_y = RingBuffer(maxlen)

    y = 100 # initial value

    fig, ax = plt.subplots()
    line, = ax.plot(data_x.all[::-1], data_y.all[::-1], linestyle='-', marker='+', color='r', markeredgecolor='b')
    #ax.set_ylim([0, 1023])
    ax.set_ylim([0, 100])

    ardu_bin_msg.ADC_calibrate(0, lambda value: limit(value, 1800.0, 24000.0, 0.0, 100.0))

    while True:
        x = datetime.datetime.utcnow()
        data = ser.readline()

        if len(data) == ardu_bin_msg.size:
            ardu_bin_msg.parse(data)
            print(ardu_bin_msg._data)
            y = ardu_bin_msg.ADC(0)
            #y = limit(y, 1800.0, 24000.0, 0.0, 100.0)
            print(x, y)
            data_x.append(x)
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
        ser.flush()

if __name__ == '__main__':
    main()
