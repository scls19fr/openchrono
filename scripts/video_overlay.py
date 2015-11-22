#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

import os
import glob
import logging
import pandas as pd

from collections import namedtuple

from PIL import Image, ImageFont, ImageDraw

COL_T = 't'

logger = logging.getLogger(__name__)

def draw_point(imagedraw, x, y, width, color):
    imagedraw.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), color)

def draw_boxed_text(imagedraw, x, y, width, height, text, text_font, text_color, box_color):
    #draw box
    y_offset = 2
    imagedraw.rectangle((x, y + y_offset, x + width, y + y_offset + height), outline=box_color, fill=box_color)
    #get size of text
    textWidth,textHeight = imagedraw.textsize(text, font=text_font)
    #draw text, putting the text in the middle of the box
    imagedraw.text((x + 5, y + ((height - textHeight) / 2)), text, font=text_font, fill=text_color)


class VideoOverlay(object):
    DATAFRAME_WIDTH = 545 #1920 #250
    DATAFRAME_HEIGHT = 800 #1080 #800

    FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"
    FONT_SIZE = 38

    TEXT_COLOR = "black"
    BACKGROUND_COLOR = "white"
    BOX_COLOR = "#c0c0c0"
    
    def __init__(self, directory, filename_data_in='data.csv'):
        self.directory = directory
        self._init_filenames(directory, filename_data_in)
        self._init_images(directory)
        
        # Set fields to display
        # None: all fields
        # []: no fields
        # ['frame', 'pos']: display fields 'frame' and 'pos' (in this order)
        self.fields = None
        
        # Default data formatter
        self.data_formatter = DataFormatter()
        
    def _init_filenames(self, directory, filename_data_in):
        self.filename_data_in = os.path.join(directory, filename_data_in)
        self.filename_video_in = os.path.join(directory, 'video.h264')
        self.filename_video_out = os.path.join(directory, 'video_overlay.h264')
        
    def _init_images(self, directory):
        # create images directory or remove images
        self.directory_images = os.path.join(directory, 'images')
        if not os.path.exists(self.directory_images):
            # create images directory
            os.makedirs(self.directory_images)
        else:        
            # remove images previously created
            for filename in glob.glob(os.path.join(self.directory_images, "*.jpg")):
                os.remove(filename)
        
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
    
    def _create_Image_and_ImageDraw(self):
        """Create a PIL.Image.Image and a PIL.ImageDraw.ImageDraw"""
        image = Image.new("RGBA", (self.DATAFRAME_WIDTH, self.DATAFRAME_HEIGHT), self.BACKGROUND_COLOR)
        image_draw = ImageDraw.Draw(image)
        return image, image_draw
    
    def _draw(self, image_draw, record):
        """Draw data (record) on a PIL.ImageDraw.ImageDraw
        and return this ImageDraw
        
        This method might be overload to customize drawing
        """
        logger.debug("draw %r on %r" % (record, image_draw))

        width, height = 330, 25
        x0, y0 = 10, 590
        
        x, y = x0, y0
        delta_x, delta_y = 0, 30
     
        if self.fields is None:
            fields = record._fields
        else:
            fields = self.fields

        for i, key in enumerate(fields):
            value = record.__dict__[key]
            text = self.data_formatter.text(key, value)
            draw_boxed_text(image_draw, x, y, width, height, text, self.font, self.TEXT_COLOR, self.BOX_COLOR)
            y += delta_y
 
        return image_draw
        
        return image_draw
    
    def _stop_frames_default(self, framenumber, framenumber_max):
        return framenumber >= framenumber_max - 1

    def _stop_frames_never(self, framenumber, framenumber_max):
        return False

    def _stop_frames(self, framenumber, framenumber_max):
        return self._stop_frames_default(framenumber, framenumber_max)
        
    def _create_missing_frames(self, framenumber, framenumber_prev, framenumber_max):
        """
        Create symbolic links between last frame and this frame
        (to avoid missing images because some frames are missing in data file)
        """
        for framenumber_missing in range(framenumber_prev + 1, framenumber):
            file1 = os.path.join(self.directory_images, self.images_fmt % framenumber_prev)
            file2 = os.path.join(self.directory_images, self.images_fmt % framenumber_missing)
            logging.debug("Create symlink between %s and %s" % (file1, file2))
            os.symlink(file1, file2)
            if self._stop_frames(framenumber_missing, framenumber_max):
                break
        
        
    def create_images(self, framenumber_max=None):
        """
        Create images with data and store them to 'images' directory
        """

        if framenumber_max is None:
            self._stop_frames = self._stop_frames_never
        else:
            self._stop_frames = self._stop_frames_default

        framenumber_prev = -1
        self._init_pil()
            
        for record in self.records:
            framenumber = record.frame
            if framenumber > framenumber_prev:
                self._create_missing_frames(framenumber, framenumber_prev, framenumber_max)
                if self._stop_frames(framenumber, framenumber_max):
                    break
                filename_image = os.path.join(self.directory_images, self.images_fmt % framenumber)
                logger.debug("Create %r" % filename_image)
                image, image_draw = self._create_Image_and_ImageDraw()
                image_draw = self._draw(image_draw, record)
                image.save(filename_image, "JPEG", quality=100)
                framenumber_prev = framenumber
    
    def create_overlay_video(self):
        raise NotImplementedError("ToDo")


class DataFormatter(object):
    def __init__(self, key_default='%s', value_default='%s', key=None, value=None):
        self.key_format_default = key_default
        self.value_format_default = value_default
        
        if key is None:
            self.d_key_format = {}
        else:
            self.d_key_format = key
        
        if value is None:
            self.d_value_format = {}
        else:
            self.d_value_format = value
     
    def _get_format(self, key, d_fmt, fmt_default):
        try:
            return d_fmt[key]
        except KeyError:
            return fmt_default
    
    def _get_value_format(self, key):
        return self._get_format(key, self.d_value_format, self.value_format_default)
    
    def _get_key_format(self, key):
        return self._get_format(key, self.d_key_format, self.key_format_default)
    
    def get_formats(self, key):
        return self._get_key_format(key), self._get_value_format(key)
     
    def _key_value_format(self, key):
        s_fmt = "%s: %s"
        return s_fmt        

    def text(self, key, value):
        s_fmt = self._key_value_format(key)
        s_key = self._get_key_format(key) % key
        s_value = self._get_value_format(key) % value
        text = s_fmt % (s_key, s_value)
        return text

class MyVideoOverlay(VideoOverlay):
    def __init__(self, *args, **kwargs):
        super(MyVideoOverlay, self).__init__(*args, **kwargs)
    
    def _draw(self, image_draw, record):
        """Draw data (record) on a PIL.ImageDraw.ImageDraw
        and return this ImageDraw
        """
        logger.debug("draw %r on %r" % (record, image_draw))

        #draw data
        x0, y0 = 10, 590
        width, height = self.DATAFRAME_WIDTH - x0, 25
        
        x, y = x0, y0
        delta_x, delta_y = 0, 30
    
        if self.fields is None:
            fields = record._fields
        else:
            fields = self.fields

        text = str(record.t)
        draw_boxed_text(image_draw, x, y, width, height, text, self.font, self.TEXT_COLOR, self.BOX_COLOR)
        y += delta_y
        for i, key in enumerate(fields):
            value = record.__dict__[key]
            text = self.data_formatter.text(key, value)
            draw_boxed_text(image_draw, x, y, width, height, text, self.font, self.TEXT_COLOR, self.BOX_COLOR)
            y += delta_y
 
        return image_draw


@click.command()
@click.argument('directory')
@click.option('--filename-data-in', default='data.csv', help='Filename data input (CSV) - data.csv or data_postprocessed.csv')
@click.option('--max-rows', default=20, help='Pandas display.max_rows')
@click.option('--max-frames', default=-1, help='Maximum number of frame')
def main(directory, filename_data_in, max_rows, max_frames):
    logging.basicConfig(level=logging.INFO)
    pd.set_option('display.max_rows', max_rows)
    
    if max_frames == -1:
        max_frames = None

    directory = os.path.expanduser(directory)

    overlay = MyVideoOverlay(directory, filename_data_in)
    
    overlay.fields = ['frame', 'pos']
    #overlay.fields = ['t0', 'pos']
    
    #overlay.data_formatter = DataFormatter()
    
    overlay.data_formatter.key_format_default = '%13s'
    #overlay.data_formatter.d_key_format = {
    #    'frame': '%s',
    #}

    #overlay.data_formatter.value_format_default = '%s'
    overlay.data_formatter.d_value_format = {
        'frame': '%06d',
        'pos': '%05.1f',
    #    't0': '%07.3f'
    }


    overlay.create_images(framenumber_max=max_frames)
    
if __name__ == '__main__':
    main()
