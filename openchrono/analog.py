#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

class AnalogInput(object):
    def __init__(self, bits_resolution=None):
        self._calibrate_func = lambda x: x  # identity
        
        self._raw_value = None
        self._value = None
        
        self.has_new_data = False
        
        self.bits_resolution = bits_resolution
        
        self._raw_value_prev = None # previous raw value
        self.has_same_raw_value = False

        self._value_prev = None # previous value
        self.has_same_value = False

    def calibrate(self, func):
        self._calibrate_func = func

    @property
    def value(self):
        self.has_new_data = False
        return self._value

    @property
    def raw(self):
        self.has_new_data = False
        return self._raw_value

    def _update(self, new_raw_val):
        self._raw_value = new_raw_val
        
        #if self._calibrate_func is not None:
        self._value = self._calibrate_func(self._raw_value)
        
        self.has_new_data = True
        
        if self._raw_value == self._raw_value_prev:
            self.has_same_raw_value = True
        else:
            self.has_same_raw_value = False

        if self._value == self._value_prev:
            self.has_same_value = True
        else:
            self.has_same_value = False
            
        self._raw_value_prev = self._raw_value
        self._value_prev = self._value
            

    def __repr__(self):
        return """AnalogInput
  value: %s
  raw: %d
""" % (self.value, self.raw)
