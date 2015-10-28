#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ArduinoBinaryMessage(object):
    def __init__(self, adc_channels_number):
        self.max_adc_channels_number = 6
        N = min(adc_channels_number, self.max_adc_channels_number)
        self.allowed_adc_channels = range(N)  # 0->N-1
        
        self.format = "BB" + "".join(["H" for i in range(N)]) + "BB"
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
