#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

import os
import logging
import pandas as pd

from collections import namedtuple

from PIL import Image, ImageFont, ImageDraw

COL_T = 't'

logger = logging.getLogger(__name__)

def draw_point(imagedraw, x, y, width, color):
    imagedraw.ellipse((x-(width/2),y-(width/2),x+(width/2),y+(width/2)), color)

def draw_boxed_text(imagedraw, x, y, width, height, text, textFont, textColour, BoxColour):
    #draw box
    imagedraw.rectangle((x, y, x+width, y+height), outline=BoxColour, fill=BoxColour)
    #get size of text
    textWidth,textHeight = imagedraw.textsize(text, font=textFont)
    #draw text, putting the text in the middle of the box
    imagedraw.text((x + 5, y + ((height - textHeight)/2)), text, font=textFont, fill=textColour)


class VideoOverlay(object):
    DATAFRAME_WIDTH = 250
    DATAFRAME_HEIGHT = 800

    FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"
    FONT_SIZE = 38

    TEXT_COLOR = "black"
    BACKGROUND_COLOR = "white"
    BOX_COLOR = "#c0c0c0"
    
    def __init__(self, directory, filename_data_in='data.csv'):
        self.directory = directory
        self._init_filenames(directory, filename_data_in)
        self._init_images(directory)     

    def _init_filenames(self, directory, filename_data_in):
        self.filename_data_in = os.path.join(directory, filename_data_in)
        self.filename_video_in = os.path.join(directory, 'video.h264')
        self.filename_video_out = os.path.join(directory, 'video_overlay.h264')
        
    def _init_images(self, directory):
        # create images directory
        self.directory_images = os.path.join(directory, 'images')
        if not os.path.exists(self.directory_images):
            os.makedirs(self.directory_images)
            
        # set images format
        self.images_fmt = "%06d.jpg"
            
    def _init_pil(self):
        self.font = ImageFont.truetype(self.FONT_PATH, self.FONT_SIZE)
        
    @property
    def records(self):
        """Returns an iterator with a namedtuple Record like: 
        
        Record(
            t=Timestamp('2015-11-21 14:46:55.161898'), 
            frame=318, 
            position=34.9397590361
 + date[:16]       )
        """
        logger.info("Reading %r" % self.filename_data_in)

        df = pd.read_csv(self.filename_data_in)
        df[COL_T] = pd.to_datetime(df[COL_T])
        df = df.set_index(COL_T)
        columns = tuple([COL_T] + list(df.columns))
        Record = namedtuple('Record', columns)
        for dat in df.itertuples():
            record = Record(*dat)
            yield(record)
    
    def _create_image(self, record):
        logger.info(record)
        #create new image
        frame = Image.new("RGBA", (self.DATAFRAME_WIDTH, self.DATAFRAME_HEIGHT), self.BACKGROUND_COLOR)
        frame_draw = ImageDraw.Draw(frame)

        #data
        #draw_boxed_text(frame_draw, 10, 590, 230, 20, "Frame %d" % record.frame,self.FONT_PATH, self.TEXT_COLOR, self.BOX_COLOR)
        
        return frame
        
    def _create_missing_frames(self, framenumber, framenumber_prev):
        """
        Create symbolic links between last frame and this frame
        (to avoid missing images because some frames are missing in data file)
        """
        for framenumber_missing in range(framenumber_prev + 1, framenumber):
            file1 = os.path.join(self.directory_images, self.images_fmt % framenumber_prev)
            file2 = os.path.join(self.directory_images, self.images_fmt % framenumber_missing)
            logging.info("Create symlink between %s and %s" % (file1, file2))
            os.symlink(file1, file2)
        
        
    def create_images(self):
        """
        Create images with data and store them to 'images' directory
        """
        framenumber_prev = -1
        self._init_pil()
        for record in self.records:
            framenumber = record.frame
            if framenumber > framenumber_prev:
                self._create_missing_frames(framenumber, framenumber_prev)
                filename_image = os.path.join(self.directory_images, self.images_fmt % framenumber)
                logger.info("Create %r" % filename_image)
                frame = self._create_image(record)
                frame.save(filename_image, "JPEG", quality=100)
                framenumber_prev = framenumber
    
    def create_overlay_video(self):
        raise NotImplementedError("ToDo")

@click.command()
@click.argument('directory')
@click.option('--filename-data-in', default='data.csv', help='Filename data input (CSV) - data.csv or data_postprocessed.csv')
@click.option('--max_rows', default=20, help='Pandas display.max_rows')
def main(directory, filename_data_in, max_rows):
    logging.basicConfig(level=logging.INFO)
    pd.set_option('display.max_rows', max_rows)

    directory = os.path.expanduser(directory)

    overlay = VideoOverlay(directory, filename_data_in)
    overlay.create_images()
    
if __name__ == '__main__':
    main()
