#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

DATA = 'data.csv'
VIDEO = 'video.h264'

class FilenameFactory(object):
    """A class to create filenames (for video or data) from a directory
    
    >>> filename = FilenameFactory("~/data/foo_dir")
    >>> filename.data
    '/home/pi/data/foo_dir/data.csv'
    >>> filename.video
    '/home/pi/data/foo_dir/video.h264'
    >>> filename.create("bar.file")
    '/home/pi/data/foo_dir/bar.file'
    """
    def __init__(self, directory, data=DATA, video=VIDEO):
        self.directory = os.path.expanduser(directory)
        self._data = data
        self._video = video

    def create(self, filename):
        filename = os.path.join(self.directory, filename)
        return filename

    @property
    def data(self):
        return self.create(self._data)

    @property
    def video(self):
        return self.create(self._video)

if __name__ == "__main__":
    import doctest
    doctest.testmod()