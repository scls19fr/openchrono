#!/usr/bin/env python
# -*- coding: utf-8 -*-

def limit(x, xmin, xmax, ymin, ymax):
    y = (ymax - ymin) / (xmax - xmin) * (x - xmin) + ymin
    if y < ymin:
        return ymin
    if y > ymax:
        return ymax
    return y
