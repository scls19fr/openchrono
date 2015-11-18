#!/usr/bin/env python
# -*- coding: utf8 -*-

import click
import picamera
import time

VIDEOFPS = 25
VIDEOHEIGHT = 1080
VIDEOWIDTH = 1920

@click.command()
@click.option('--vflip/--no-vflip', default=False, help="Video vertical flip")
@click.option('--hflip/--no-hflip', default=False, help="Video horizontal flip")
@click.option('--video-stabilization/--no-video-stabilization', default=True, help="Video stabilization")
@click.option('--video-filename', default='vid.h264', help="Video filename (open with omxplayer)")
@click.option('--video-preview/--no-video-preview', default=True, help="Video preview")
def main(vflip, hflip, video_stabilization, video_filename, video_preview):
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
            camera.start_recording(video_filename) #, inline_headers=False)
            print("Recording - started pi camera")
            try:
                while(True):
                    print("data in the loop")
                    #framenumber = camera.frame
                    #print(framenumber)
                    time.sleep(0.1)

            except KeyboardInterrupt:
                print("User Cancelled (Ctrl C)")
                camera.stop_recording()
                if video_preview:
                    camera.stop_preview()

if __name__ == "__main__":
    main()

