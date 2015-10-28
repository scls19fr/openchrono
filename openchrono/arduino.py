#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import struct
import serial
import time

logger = logging.getLogger(__name__)

class ArduinoBinaryMessage(object):
    def __init__(self, adc_channels_number):
        self.max_adc_channels_number = 6
        self.adc_channels_number = min(adc_channels_number, self.max_adc_channels_number)
        self.allowed_adc_channels = range(N)  # 0->N-1
        
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

    def _ADC_raw(self, channel):       
        if channel in self.allowed_adc_channels:
            return self._data[2 + channel]
        else:
            raise Exception("channel=%s must be in %s" % (channel, self.allowed_adc_channels))
        
    def ADC(self, channel):
        value = self._ADC_raw(channel)
        if channel in self._d_calibrate_funcs.keys():
            calibrate_func = self._d_calibrate_funcs[channel]
            return calibrate_func(value)
        else:
            return value

    def ADC_calibrate(self, channel, calibrate_func):
        assert channel in self.allowed_adc_channels, \
            "channel=%s must be in %s" % (channel, self.allowed_adc_channels)
        self._d_calibrate_funcs[channel] = calibrate_func

class SensorsHardware(object):
    def __init__(self, *args, **kwargs):
        pass

    def connect(self):
        pass

    def read(self):
        pass

    def get(self, key):
        return self._data[key]

class SensorsArduino(SensorsHardware):
    def __init__(self, device, baudrate, adc_channels_number):
        super(SensorsArduino, self).__init__(device, baudrate)
        self._name = "Arduino"
        self._device = device
        self._baudrate = baudrate
        self._bin_msg = ArduinoBinaryMessage(adc_channels_number=adc_channels_number)

    def connect(self):
        self._ser = serial.Serial(device, baudrate)

        # reset the arduino
        self._ser.setDTR(level=False)
        time.sleep(0.5)
        # ensure there is no stale data in the buffer
        self._ser.flushInput()
        self._ser.setDTR()
        time.sleep(0.5)

        print("Waiting for %s %s @ %d bauds..." % (self._name, self._device, self._baudrate))

        # initial handshake w/ arduino
        allowed_byte = 0x07
        while True:
            byte_received = struct.unpack("B", ser.read())[0]
            print("Handshake: %s" % byte_received)
            if byte_received == allowed_byte:
                break
        self._ser.flushInput()
        self._ser.write(b'\x10')

        print("Connected to %s %s" % (self._name, self._device))

    def read(self):
        raw_data = self._ser.readline()
        length, expected_length = len(raw_data), self._bin_msg.size
        if length == expected_length:
            self._bin_msg.parse(data)
            return True
        else:
            raise Exception("Incorrect length %d != %d" % (length, expected_length))

    def get(self, key):
        raise NotImplementedError("ToDo")