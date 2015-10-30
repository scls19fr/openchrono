#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml

def load_config():
    filename = "openchrono.yaml"
    with open(filename, 'r') as stream:
        d = yaml.load(filename)
    return d

def main():
    print(load_config())

if __name__ == '__main__':
    main()
