#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import os
from os.path import expanduser
from collections import OrderedDict

HOME = expanduser("~")

def _load_config_file(filename):
    if filename is None:
        filename = os.path.join(HOME, ".openchrono.yaml")
    with open(filename, 'r') as f:
        config = yaml.load(f)
    return config

def _process_config(config):
    if "sensors" in config.keys():
        config["sensors"] = OrderedDict(config["sensors"])
    return config

def _sample_config():
    s_config = """---
sensors: 
  - 
    - "sensor00"
    - 
        hw_type: "arduino"
        device: "/dev/ttyUSB0"
        baudrate: 57600
"""
    return yaml.load(s_config)

def load_config(filename=None):
    config = _load_config_file(filename)
    config = _process_config(config)
    return config

def main():
    config = load_config()
    print(config)
    print(config["sensors"]["sensor00"])
    for sensor_name, sensor_config in config["sensors"].items():
        print(sensor_name, sensor_config)

if __name__ == '__main__':
    main()
