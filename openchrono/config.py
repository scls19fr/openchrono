#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import os
from os.path import expanduser

HOME = expanduser("~")

def load_config():
    filename = os.path.join(HOME, ".openchrono.yaml")
    with open(filename, 'r') as f:
        d = yaml.load(f)
    return d

def main():
    print(load_config())

if __name__ == '__main__':
    main()
