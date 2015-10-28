#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    def read(self):
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


class SensorsArduino(SensorsHardware):
    def __init__(self, device, baudrate, adc_channels_number, read_error_exception=False):
        super(SensorsArduino, self).__init__(device, baudrate)
        self._name = "Arduino"
        self._device = device
        self._baudrate = baudrate
        self._bin_msg = _ArduinoBinaryMessage(adc_channels_number=adc_channels_number)
        self._ADC = [AnalogInput() for i in range(adc_channels_number)]
        self._capabilities = ["ADC%d" % i for i in range(adc_channels_number)]

        if read_error_exception:
            self._read_error = self._read_error_raise_exception
        else:
            self._read_error = self._read_error_no_exception

    def connect(self):
        self._ser = serial.Serial(self._device, self._baudrate)

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

        logger.info("Connected to %s %s" % (self._name, self._device))

    def read(self):
        raw_data = self._ser.readline()
        length, expected_length = len(raw_data), self._bin_msg.size
        if length == expected_length:
            self._bin_msg.parse(raw_data)
            self._update()
            return True
        else:
            return self._read_error(length, expected_length)

    def _read_error_no_exception(self, length, expected_length):
        return False
        
    def _read_error_raise_exception(self, length, expected_length):
        raise Exception("Incorrect length %d != %d" % (length, expected_length))

    def _update(self):
        for channel, adc in enumerate(self._ADC):
            self._ADC[channel]._update(self._bin_msg.ADC(channel))

    def get(self, key):
        raise NotImplementedError("ToDo")

    @property
    def ADC(self):
        return self._ADC
