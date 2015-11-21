#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

CSV_DEFAULT_SEP = ','
CSV_DEFAULT_LF = '\n'

def append_same_length(columns, data):
    if columns != []:
        return len(columns) == len(data)
    return True

class DataBuffer(object):
    def __init__(self, csv_filename, columns=None, csv_sep=CSV_DEFAULT_SEP, csv_lf=CSV_DEFAULT_LF):
        self._fd = open(csv_filename, "w")
        
        self.csv_sep = csv_sep
        self.csv_lf = csv_lf
        
        if columns is None:
            self._columns = []
        else:
            self._columns = columns
    
    @property
    def columns(self):
        return self._columns
    
    @columns.setter
    def columns(self, value):
        self._columns = value
        self._append_columns()
    
    def _append_columns(self):
        if self.columns != []:
            self.append(*self.columns)
    
    def append(self, *data):
        assert append_same_length(self.columns, data), "data and columns must have same length"
        s = self.csv_sep.join(map(lambda x: str(x), data)) + self.csv_lf
        self._fd.write(s)
    
    def close(self):
        self._fd.close()
    
    #def to_csv(self, filename):
    #    pass
    
    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        self.close()


def main():
    data = DataBuffer("data.csv")
    data.columns = ["a", "b", "c"]
    data.append(1, 2.5, 3)
    data.append(4, 5, 6)
    data.append(7, 8, 9)
    data.close()

def main_with_context_manager():
    """
    Using a context manager (with ...) will
    automatically close file descriptor
    """
    with DataBuffer("data.csv") as data:
        data.columns = ["a", "b", "c"]
        data.append(1, 2.5, 3)
        data.append(4, 5, 6)
        data.append(7, 8, 9)
        
if __name__ == '__main__':
    main_with_context_manager()