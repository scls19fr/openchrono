#!/usr/bin/env python
# -*- coding: utf8 -*-

import click

import os
import picamera
import time
import datetime

import logging
import traceback

from openchrono.databuffer import DataBuffer
from openchrono.arduino import SensorsArduino
from openchrono.utils import linear_function_with_limit
from openchrono.filename import FilenameFactory

import pingo
from pingo.parts.led import Led
from pingo.parts.button import Switch
import threading

logger = logging.getLogger(__name__)

VIDEO_FPS = 25
VIDEO_HEIGHT = 1080
VIDEO_WIDTH = 1920


class RecordingTask(threading.Thread):
    def __init__(self, camera, sensors, filename, video_preview, erase, time_to_sleep):
        threading.Thread.__init__(self)
        
        self.camera = camera
        self.sensors = sensors
        
        self.filename = filename
        self.video_preview = video_preview
        self.erase = erase
        
        self.time_to_sleep = time_to_sleep
        
        self.active = False
    
    def run(self):
        self.active = True

        self.filename.new_recording()
        
        if not self.erase:
            data_folder = self.filename.recording_directory
            if not os.path.exists(data_folder):
                os.makedirs(data_folder)
        
        if self.video_preview:
            self.camera.start_preview()
        
        with DataBuffer(self.filename.data) as data:
            data.columns = ["t", "frame", "pos"]
            
            self.camera.start_recording(self.filename.video) #, inline_headers=False)
            logger.info("Recording to %s" % self.filename.video)
            while(self.active):
                now = datetime.datetime.utcnow()
                
                logger.info("data in the loop @ %s" % now)
                
                framenumber = self.camera.frame.index
                #logger.info(framenumber)
                
                to_append = False
                ai0 = self.sensors[0].ADC[0]
                if self.sensors[0].update() and not ai0.has_same_value: #and ai0.has_new_data: #ai0.has_same_raw_value
                    to_append = True
                
                if to_append:
                    data.append(now, framenumber, ai0.value) # ai0.raw or ai0.value
                
                time.sleep(self.time_to_sleep)

            self._when_stopped()


    def terminate(self):
        self.active = False
    
    def _when_stopped(self):
        logger.info(" Stop recording %s" % self.filename.video)
        self.camera.stop_recording()
        self.recording = False
        if self.video_preview:
            self.camera.stop_preview()
        logger.info(" stopped")        
        


class RecorderApp(object):
    def __init__(self, filename, vflip, hflip, video_stabilization, 
                 video_preview, device, baudrate, erase, fps, height, width):
        self.filename = filename  # filename factory (to create filenames)
        
        self.board = pingo.detect.get_board()

        led_pin = self.board.pins[13]
        self.led = Led(led_pin)

        btn_pin = self.board.pins[7]
        self.switch = Switch(btn_pin)
        self.switch.set_callback_up(self.toggle_recording)
        
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
        self.recording_task = None
        
        self.sensors = []
        
        sensors_arduino = SensorsArduino(device=self.device, baudrate=self.baudrate, adc_channels_number=2)
        logger.info("capabilities: %s" % sensors_arduino.capabilities)
        sensors_arduino.connect()
        sensors_arduino.ADC[0].calibrate(lambda value: linear_function_with_limit(value, 520.0, 603.0, 0.0, 100.0))
        
        self.sensors.append(sensors_arduino)


    def toggle_recording(self):
        print("switch press")
        self.recording = not self.recording

        if self.recording:
            print("Start recording")
            self.recording_task = RecordingTask(self.camera, self.sensors, self.filename, 
                self.video_preview, self.erase, self.time_to_sleep)
            self.recording_task.start()
            self.led.blink(times=0, on_delay=0.8, off_delay=0.2) # blink foreever

        else:
            print("Stop recording")
            self.recording_task.terminate()
            self.led.stop() # stop blinking
            #while(self.led.blinking):
            #    print("waiting led stop blinking")
            #    time.sleep(0.5)
            #    self.led.stop()
            self.led.on()  # ToFix !!!

    def init_led_and_switch(self):
        self.led.on()        
        self.switch.start()
    
    def loop(self):
        self.init_led_and_switch()
        try:
            while(True):
                logger.info("mainloop")
                time.sleep(3)
        except KeyboardInterrupt:
            logger.info("User Cancelled (Ctrl C)")
        finally:
            self.close()
            
        
    def close(self):
        if self.recording:
            self.recording = False
            self.recording_task.terminate()

        self.camera.close()

        self.led.off()
        self.switch.stop()
        self.led.stop()
        self.board.cleanup()
        
        logger.info("closed RecorderApp")


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
  
    logging.basicConfig(level=logging.INFO)

    data_folder = os.path.expanduser(data_folder)
    
    filename = FilenameFactory(data_folder, data=data_filename, video=video_filename)
    
    app = RecorderApp(filename, vflip, hflip, video_stabilization, 
        video_preview, device, baudrate, erase, fps, height, width)
    
    app.loop()
    #app.recording = True
    #app.start_recording()
    


if __name__ == "__main__":
    main()

