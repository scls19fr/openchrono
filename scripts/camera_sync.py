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

VIDEOFPS = 25
VIDEOHEIGHT = 1080
VIDEOWIDTH = 1920

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
def main(vflip, hflip, video_stabilization, data_folder, data_filename, video_filename, video_preview, 
    device, baudrate, erase):
    s_now = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
    
    data_folder = os.path.expanduser(data_folder)
    
    if not erase:
        data_folder = os.path.join(data_folder, s_now)
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)


    sensors00 = SensorsArduino(device=device, baudrate=baudrate, adc_channels_number=2)
    print("capabilities: %s" % sensors00.capabilities)
    sensors00.connect()
    sensors00.ADC[0].calibrate(lambda value: linear_function_with_limit(value, 520.0, 603.0, 0.0, 100.0))

    
    with picamera.PiCamera() as camera:
        #turn LED on
        #led.on()

        #setup camera
        camera.resolution = (VIDEOWIDTH, VIDEOHEIGHT)
        camera.framerate = VIDEOFPS
        camera.vflip = vflip
        camera.hflip = hflip
        camera.video_stabilization = video_stabilization

        if video_preview:
            camera.start_preview()
        
        with DataBuffer(os.path.join(data_folder, data_filename)) as data:
            data.columns = ["t", "frame", "pos"]
            
            camera.start_recording(os.path.join(data_folder, video_filename)) #, inline_headers=False)
            print("Recording - started pi camera")
            try:
                while(True):
                    now = datetime.datetime.utcnow()
                    
                    print("data in the loop @ %s" % now)
                    
                    framenumber = camera.frame.index
                    print(framenumber)
                    
                    to_append = False
                    ai0 = sensors00.ADC[0]
                    if sensors00.update() and not ai0.has_same_value: #and ai0.has_new_data: #ai0.has_same_raw_value
                        to_append = True
                    
                    if to_append:
                        data.append(now, framenumber, ai0.value) # ai0.raw or ai0.value
                    
                    time.sleep(0.01)

            except KeyboardInterrupt:
                print("User Cancelled (Ctrl C)")
                camera.stop_recording()
                if video_preview:
                    camera.stop_preview()

if __name__ == "__main__":
    main()

