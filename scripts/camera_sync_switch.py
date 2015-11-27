#!/usr/bin/env python
# -*- coding: utf8 -*-

import click

import os
import picamera
import time
import datetime

from openchrono.databuffer import DataBuffer
from openchrono.arduino import SensorsArduino
from openchrono.utils import linear_function_with_limit
from openchrono.filename import FilenameFactory


VIDEO_FPS = 25
VIDEO_HEIGHT = 1080
VIDEO_WIDTH = 1920


class RecorderApp(object):
    def __init__(self, filename, vflip, hflip, video_stabilization, 
                 video_preview, device, baudrate, erase, fps, height, width):
        self.filename = filename  # filename factory (to create filenames)
        
        self.camera = picamera.PiCamera()
        
        self.camera.resolution = (width, height)
        self.camera.framerate = fps
        self.camera.vflip = vflip
        self.camera.hflip = hflip
        self.camera.video_stabilization = video_stabilization

        self.video_preview = video_preview
        self.device = device
        self.baudrate = baudrate
        self.erase = erase
        
        self.time_to_sleep = 0.01
        
        self.recording = False
        
        self.sensors = []
        
        sensors_arduino = SensorsArduino(device=self.device, baudrate=self.baudrate, adc_channels_number=2)
        print("capabilities: %s" % sensors_arduino.capabilities)
        sensors_arduino.connect()
        sensors_arduino.ADC[0].calibrate(lambda value: linear_function_with_limit(value, 520.0, 603.0, 0.0, 100.0))
        
        self.sensors.append(sensors_arduino)

    
    def loop(self):
        while(True):
            print("loop")
            self.start_recording()
            
    
    
    def start_recording(self):
        self.filename.new_recording()
        
        if not self.erase:
            data_folder = self.filename.recording_directory
            if not os.path.exists(data_folder):
                os.makedirs(data_folder)


        
        #turn LED on
        #led.on()

        #setup camera

        if self.video_preview:
            self.camera.start_preview()
        
        with DataBuffer(self.filename.data) as data:
            data.columns = ["t", "frame", "pos"]
            
            self.camera.start_recording(self.filename.video) #, inline_headers=False)
            print("Recording to %s" % self.filename.video)
            try:
                while(self.recording):
                    now = datetime.datetime.utcnow()
                    
                    print("data in the loop @ %s" % now)
                    
                    framenumber = self.camera.frame.index
                    #print(framenumber)
                    
                    to_append = False
                    ai0 = self.sensors[0].ADC[0]
                    if self.sensors[0].update() and not ai0.has_same_value: #and ai0.has_new_data: #ai0.has_same_raw_value
                        to_append = True
                    
                    if to_append:
                        data.append(now, framenumber, ai0.value) # ai0.raw or ai0.value
                    
                    time.sleep(self.time_to_sleep)

            except KeyboardInterrupt:
                print("User Cancelled (Ctrl C)")
            finally:
                self.stop_recording()

    
    def stop_recording(self):
        print("stop recording")
        self.camera.stop_recording()
        if self.video_preview:
            self.camera.stop_preview()
        self.camera.close()
    
    def close(self):
        self.camera.close()

@click.command()
@click.option('--vflip/--no-vflip', default=False, help="Video vertical flip")
@click.option('--hflip/--no-hflip', default=False, help="Video horizontal flip")
@click.option('--video-stabilization/--no-video-stabilization', default=True, help="Video stabilization")
@click.option('--data-folder', default='~/data', help="Data folder")
@click.option('--data-filename', default='data.csv', help="Data filename (CSV file)")
@click.option('--video-filename', default='video.h264', help="Video filename (open with omxplayer)")
@click.option('--video-preview/--no-video-preview', default=True, help="Video preview")
@click.option('--device', default='/dev/ttyUSB0', help='device')
@click.option('--baudrate', default=57600, help='Baudrate (9600 14400 19200 28800 38400 57600 115200) - default to 57600')
@click.option('--erase/--no-erase', default=False, help='Erase data (video and csv)')
@click.option('--fps', default=VIDEO_FPS, help='Frame per second (default: %d)' % VIDEO_FPS)
@click.option('--height', default=VIDEO_HEIGHT, help='Video height (default: %d)' % VIDEO_HEIGHT)
@click.option('--width', default=VIDEO_WIDTH, help='Video width (default: %d)' % VIDEO_WIDTH)
def main(vflip, hflip, video_stabilization, data_folder, data_filename, video_filename, video_preview, 
    device, baudrate, erase, fps, height, width):
  
    data_folder = os.path.expanduser(data_folder)
    
    filename = FilenameFactory(data_folder, data=data_filename, video=video_filename)
    
    app = RecorderApp(filename, vflip, hflip, video_stabilization, 
        video_preview, device, baudrate, erase, fps, height, width)
    
    #app.loop()
    app.recording = True
    app.start_recording()
    


if __name__ == "__main__":
    main()

