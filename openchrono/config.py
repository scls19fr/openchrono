#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import os
from os.path import expanduser
from collections import OrderedDict

HOME = expanduser("~")

def load_config(filename=None):
    if filename is None:
        filename = os.path.join(HOME, ".openchrono.yaml")
    with open(filename, 'r') as f:
        config = yaml.load(f)
    if "hardware" in config.keys():
        config["hardware"] = OrderedDict(config["hardware"])
    return config

def main():
    config = load_config()
    print(config)
    print(config["hardware"]["sensor00"])

if __name__ == '__main__':
    main()
