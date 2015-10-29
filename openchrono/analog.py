#!/usr/bin/env python
# -*- coding: utf-8 -*-

class AnalogInput(object):
    def __init__(self):
        self._func = None
        self._raw_value = None
        self._value = None
        self.has_new_data = False

    def calibrate(self, func):
        self._func = func

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
        if self._func is not None:
            self._value = self._func(self._raw_value)
        self.has_new_data = True

    def __repr__(self):
        return """AnalogInput
  value: %s
  raw: %d
""" % (self.value, self.raw)
