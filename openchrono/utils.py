#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

def linear_function_with_limit(x, xmin, xmax, ymin, ymax):
    y = (ymax - ymin) / (xmax - xmin) * (x - xmin) + ymin
    if y < ymin:
        return ymin
    if y > ymax:
        return ymax
    return y

def limit(x, xmin, xmax):
    if x < xmin:
        return xmin
    if x > xmax:
        return xmax
    return x
