#!/usr/bin/env python
# -*- coding: utf-8 -*-

class AnalogInput(object):
    def __init__(self):
        self._func = None
        self._raw_value = None
        self._value = None

    def calibrate(self, func):
        self._func = func

    @property
    def value(self):
        return self._value

    @property
    def raw(self):
        return self._raw_value

    def _update(self, new_raw_val):
        self._raw_value = new_raw_val
        if self._func is not None:
            self._value = self._func(self._raw_value)
