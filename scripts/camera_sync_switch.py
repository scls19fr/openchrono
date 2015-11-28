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
#from pingo.parts.led import Led
from pingo.parts.button import Switch


class Led(object):
    """A single LED"""

    def __init__(self, pin, lit_state=pingo.HIGH):
        """Set lit_state to pingo.LOW to turn on led by bringing
           cathode to low state.

        :param lit_state: use pingo.HI for anode control, pingo.LOW
                          for cathode control
        """

        pin.mode = pingo.OUT
        self.pin = pin
        self.lit_state = lit_state
        self.blink_task = None

    def on(self):
        if self.lit_state == pingo.HIGH:
            self.pin.high()
        else:
            self.pin.low()

    def off(self):
        if self.lit_state == pingo.HIGH:
            self.pin.low()
        else:
            self.pin.high()

    @property
    def lit(self):
        return self.pin.state == self.lit_state

    @lit.setter
    def lit(self, new_state):
        if new_state:
            self.on()
        else:
            self.off()

    @property
    def blinking(self):
        return self.blink_task is not None and self.blink_task.active

    def toggle(self):
        self.pin.toggle()

    def blink(self, times=3, on_delay=.5, off_delay=None):
        """
        :param times: number of times to blink (0=forever)
        :param on_delay: delay while LED is on
        :param off_delay: delay while LED is off
        """
        if self.blinking:
            self.stop()
        self.blink_task = BlinkTask(self, times, on_delay, off_delay)
        threading.Thread(target=self.blink_task.run).start()

    def stop(self):
        """Stop blinking"""
        if self.blinking:
            self.blink_task.terminate()
            self.blink_task = None

class BlinkTask(object):

    def __init__(self, led, times, on_delay, off_delay):
        """
        :param led: Led instance to to blink
        :param times: number of times to blink (0=forever)
        :param on_delay: delay while LED is on
        :param off_delay: delay while LED is off
        """
        self.led = led
        self.led_initial_pin_state = self.led.pin.state
        self.active = True
        self.forever = times == 0
        self.times_remaining = times
        self.on_delay = on_delay
        self.off_delay = off_delay if off_delay is not None else on_delay
        self.led.off()

    def terminate(self):
        self.active = False

    def run(self):
        while self.active and (self.forever or self.times_remaining):
            self.led.toggle()
            if self.led.lit:
                time.sleep(self.on_delay)
                if not self.forever:
                    self.times_remaining -= 1
            else:
                time.sleep(self.off_delay)
        else:
            self.led.pin.state = self.led_initial_pin_state
            self.active = False

import threading

logger = logging.getLogger(__name__)

VIDEO_FPS = 25
VIDEO_HEIGHT = 1080
VIDEO_WIDTH = 1920


class RecordingTask(threading.Thread):
    def __init__(self, camera_settings, sensors, filename, video_preview, erase, time_to_sleep):
        threading.Thread.__init__(self)
        
        self.camera = picamera.PiCamera()
        camera_settings.apply_to(self.camera)
        
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
                
                #logger.info("data in the loop @ %s" % now)
                
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
        self.camera.close()
        logger.info(" stopped")        
        
class Settings(object):
    """
    A generic class to apply a dict to an instance object
    """
    
    def __init__(self, **settings):
        self._settings = settings
    
    def apply_to(self, obj):
        for key, value in self._settings.iteritems():
            try:
                setattr(obj, key, value)
                print(key, value)
            except Exception as e:
                #logging.error(traceback.format_exc())
                raise e

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
        
        
        self.camera_settings = Settings(
            resolution = (width, height),
            framerate = fps,
            vflip = vflip,
            hflip = hflip,
            video_stabilization = video_stabilization
        )
   
        
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
            self.recording_task = RecordingTask(self.camera_settings, self.sensors, self.filename, 
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
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("User Cancelled (Ctrl C)")
        finally:
            self.close()
            
        
    def close(self):
        if self.recording:
            self.recording = False
            self.recording_task.terminate()

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

