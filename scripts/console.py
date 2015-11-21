#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import time
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

    t_last = datetime.datetime.utcnow()
    while True:
        t = datetime.datetime.utcnow()
        try:
            if sensors00.update() and sensors00.ADC[0].has_new_data:
                print(sensors00._bin_msg._data)
                ai0 = sensors00.ADC[0]
                y_raw = ai0.raw
                y = ai0.value
                logger.info("%s %s %s" % (t, y, t - t_last))
        except Exception as e:
            logger.error(traceback.format_exc())
            #raise e
        t_last = t

if __name__ == '__main__':
    main()
