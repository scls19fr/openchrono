#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import click

import logging
import struct
import serial
import time

from analog import AnalogInput

logger = logging.getLogger(__name__)


class SensorsHardware(object):
    def __init__(self, *args, **kwargs):
        self._capabilities = []

    def connect(self):
        pass

    def update(self):
        pass

    def get(self, key):
        return self._data[key]

    @property
    def capabilities(self):
        return self._capabilities

    
class _ArduinoBinaryMessage(object):
    def __init__(self, adc_channels_number):
        self.max_adc_channels_number = 6
        self.adc_channels_number = min(adc_channels_number, self.max_adc_channels_number)
        self.allowed_adc_channels = range(self.adc_channels_number)  # 0->N-1
        
        self.format = "BB" \
            + "".join(["H" for i in range(self.adc_channels_number)]) \
            + "BB"
        self._size = struct.calcsize(self.format)
        
        self._d_calibrate_funcs = {}
        
        self._data = None
        
    def parse(self, raw_data):
        self._raw_data = raw_data
        self._data = struct.unpack(self.format, raw_data)

    @property
    def size(self):
        return self._size

    def ADC(self, channel):       
        if channel in self.allowed_adc_channels:
            return self._data[2 + channel]
        else:
            raise Exception("channel=%s must be in %s" % (channel, self.allowed_adc_channels))

import threading


class SensorThread(threading.Thread):
    def __init__(self, sensor, time_to_sleep):
        threading.Thread.__init__(self)
        
        self.sensor = sensor
        self.time_to_sleep = time_to_sleep

        #set to not running
        self.running = False

        #self.update()
        
    def stop(self):
        self.running = False            

    def restart(self):
        if not self.running:
            self.running = True
        else:
            raise Exception("Can't restart - thread was ever running")
    
    def run(self):
        #loop until it's set to stopped
        self.running = True
        while(self.running):
            #update data
            self.sensor.update()
            #sleep
            time.sleep(self.time_to_sleep)
        self.running = False
    
    def update(self):
        raise NotImplementedError("Must be implmented in inherit class")


class SensorsArduino(SensorsHardware):
    def __init__(self, device, baudrate, adc_channels_number, time_to_sleep=0.002, update_error_exception=False):
        
        super(SensorsArduino, self).__init__(device, baudrate)
        self._name = "Arduino"
        self._device = device
        self._baudrate = baudrate
        self._timeout = 1
        self._bin_msg = _ArduinoBinaryMessage(adc_channels_number=adc_channels_number)
        self._ADC = [AnalogInput(bits_resolution=10) for i in range(adc_channels_number)]
        self._capabilities = ["ADC%d" % i for i in range(adc_channels_number)]
        
        self.thread = SensorThread(self, time_to_sleep)

        if update_error_exception:
            self._update_error = self._update_error_raise_exception
        else:
            self._update_error = self._update_error_no_exception

    def connect(self):
        self._ser = serial.Serial(self._device, self._baudrate, timeout=self._timeout)

        # reset the arduino
        self._ser.setDTR(level=False)
        time.sleep(0.5)
        # ensure there is no stale data in the buffer
        self._ser.flushInput()
        self._ser.setDTR()
        time.sleep(0.5)

        logger.info("Waiting for %s %s @ %d bauds..." % (self._name, self._device, self._baudrate))

        # initial handshake w/ arduino
        allowed_byte = 0x07
        while True:
            byte_received = struct.unpack("B", self._ser.read())[0]
            logger.info("Handshake: %s" % byte_received)
            if byte_received == allowed_byte:
                break
        self._ser.flushInput()
        self._ser.write(b'\x10')
        #self._ser.flushInput()

        logger.info("Connected to %s %s" % (self._name, self._device))

    def update(self):
        #print("update")
        raw_data = self._ser.readline()
        length, expected_length = len(raw_data), self._bin_msg.size
        if length == expected_length:
            self._bin_msg.parse(raw_data)
            self._update_channels()
            self._ser.flushInput()
            return True
        else:
            return self._update_error(length, expected_length)

    def _update_error_no_exception(self, length, expected_length):
        return False
        
    def _update_error_raise_exception(self, length, expected_length):
        raise Exception("Incorrect length %d != %d" % (length, expected_length))

    def _update_channels(self):
        for channel, adc in enumerate(self._ADC):
            self._ADC[channel]._update(self._bin_msg.ADC(channel))

    def get(self, key):
        raise NotImplementedError("ToDo")

    @property
    def ADC(self):
        return self._ADC

def main_without_thread(device, baudrate, update_error_exception):
    import datetime
    import traceback
    from utils import linear_function_with_limit
    
    logging.basicConfig(level=logging.INFO)
    
    sensors00 = SensorsArduino(device=device, baudrate=baudrate, adc_channels_number=2, update_error_exception=update_error_exception)
    print("capabilities: %s" % sensors00.capabilities)
    sensors00.connect()
    sensors00.ADC[0].calibrate(lambda value: linear_function_with_limit(value, 520.0, 603.0, 0.0, 100.0))
    
    #start up sensors controller thread
    #sensors00.start()

    t_last = datetime.datetime.utcnow()
    try:
        while True:
            t = datetime.datetime.utcnow()
            if sensors00.update() and sensors00.ADC[0].has_new_data:
                print(sensors00._bin_msg._data)
                ai0 = sensors00.ADC[0]
                y_raw = ai0.raw
                y = ai0.value
                logger.info("%s %s %s" % (t, y, t - t_last))
            t_last = t
    except KeyboardInterrupt:
        print("Cancelled by user (CTRL+C)")
    except Exception as e:
        logger.error(traceback.format_exc())
        #raise e
    finally:
        print("Stopping sensors controller")
    
    print("Done")
    
    return

def main_with_thread(device, baudrate, update_error_exception):
    import datetime
    import traceback
    from utils import linear_function_with_limit
    
    logging.basicConfig(level=logging.INFO)
    
    sensors00 = SensorsArduino(device=device, baudrate=baudrate, adc_channels_number=2, update_error_exception=update_error_exception)
    print("capabilities: %s" % sensors00.capabilities)
    sensors00.connect()
    sensors00.ADC[0].calibrate(lambda value: linear_function_with_limit(value, 520.0, 603.0, 0.0, 100.0))
    
    #start up sensors controller thread
    sensors00.thread.start()
    sensors00.thread.running = True

    t_last = datetime.datetime.utcnow()
    try:
        while True:
            t = datetime.datetime.utcnow()
            print(sensors00._bin_msg._data)
            ai0 = sensors00.ADC[0]
            y_raw = ai0.raw
            y = ai0.value
            logger.info("%s %s %s" % (t, y, t - t_last))
            t_last = t
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("Cancelled by user (CTRL+C)")
    except Exception as e:
        logger.error(traceback.format_exc())
        #raise e
    finally:
        print("Stopping sensors controller (and thread)")
        #stop the controller
        sensors00.thread.stop()
        #wait for the tread to finish if it hasn't already
        sensors00.thread.join()        
    
    print("Done")
    
    return

@click.command()
@click.option('--device', default='/dev/ttyUSB0', help='device')
@click.option('--baudrate', default=57600, help='Baudrate (9600 14400 19200 28800 38400 57600 115200) - default to 57600')
@click.option('--thread/--no-thread', default=False, help='Run with or without thread')
@click.option('--error-exception/--no-error-exception', default=False, help='Raise exception on update error')

def main(device, baudrate, thread, error_exception):
    if not thread:
        return main_without_thread(device, baudrate, error_exception)
    else:
        return main_with_thread(device, baudrate, error_exception)

if __name__ == '__main__':
    main()

