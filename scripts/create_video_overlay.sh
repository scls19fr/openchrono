#!/usr/bin/env bash

#pass in an input directory where the video.h264 and data.csv files are
#and an output directory where the videos should be created

INPUTDIR=$1
OUTPUTDIR=$2 #ToDo: if no $2 use $1
SCRIPTDIR=$(dirname $0)/

echo "Creating Videos $SCRIPTDIR $INPUTDIR $OUTPUTDIR DONE"

#create data images
echo "  Creating data images"
#python ${SCRIPTDIR}video_overlay.py ${INPUTDIR}

#create data video
echo "  Create data video"
#delete data video (if it exists)
#rm ${OUTPUTDIR}data.avi

# Don't forget to install mencoder using
# sudo apt-get install mplayer
#mencoder "mf://${INPUTDIR}*.jpg" -mf fps=25 -o ${OUTPUTDIR}data.avi -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=800000

# Don't forget to install avconv using
# sudo apt-get install libav-tools
#avconv -r 10 -i ${INPUTDIR}images/%06d.jpg -r 10 -vcodec libx264 -crf 20 -g 15 ${OUTPUTDIR}data.mp4

#echo "  Deleting data images"
#rm ${INPUTDIR}images/*.jpg

#mp4 video
#echo "  Creating mp4 of video"
#delete mp4 video (if it exists)
#rm ${OUTPUTDIR}video.mp4

# Don't forget to install MP4Box
# sudo apt-get install gpac
#MP4Box -add $INPUTDIR/video.h264 $OUTPUTDIR/vid.mp4
#MP4Box -add $INPUTDIR/video.h264 vid.mp4

