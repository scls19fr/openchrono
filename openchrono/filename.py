#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

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
    def __init__(self, data_directory, recording_subdirectory="", data=DATA, video=VIDEO):
        self.data_directory = os.path.expanduser(data_directory)
        self._recording_subdirectory = recording_subdirectory
        self._data = data
        self._video = video

    def create(self, filename):
        filename = os.path.join(self.data_directory, self.recording_directory, filename)
        return filename

    @property
    def data(self):
        return self.create(self._data)

    @property
    def video(self):
        return self.create(self._video)
    
    @property
    def recording_directory(self):
        return os.path.join(self.data_directory, self._recording_subdirectory)
    
    def new_recording(self):
        self._recording_subdirectory = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")        

if __name__ == "__main__":
    import doctest
    doctest.testmod()