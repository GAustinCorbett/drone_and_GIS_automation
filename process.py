#!/usr/bin/python3
#   An ugly hacky script to take a gopro MP4 file as commandline input
#   and output extracted images with timestamps and gps data in exif data
#  Assumes that it's all there!

# requires linux with ffmpeg, ffprobe, gopro2gpx, gpscorrelate
# python libraries: piexif, gpxpy  (actually gopro2gpx IS a python utility)
# Can probably replace system calls with python ffmpeg bindings to be cleaner   

import sys
import os
import piexif as pe
#import pytz
from datetime import datetime, timedelta
import gpxpy
import gpxpy.gpx


def run_gopro2gpx(infile, outfile): #There's got to be a better way to do this
    
    #   Run gopro2gpx on MP4 to extract kml and gpx file
    os.system("python3 -m gopro2gpx " + str(infile) + " " + outfile)


def extract_images(infile):
    
    #   Extract image frames and save filenames to images.txt.
    os.system("mkdir ./extracted_images")

    #This is slow and trivial.  There's probably a better way using seeking function
    os.system("ffmpeg -i " + str(infile) +
              " -r " + str(r) +
              " extracted_images/image-%04d.jpeg") 
    os.system("ls -1 ./extracted_images/*.jpeg>images.txt")
    
    #  Extract frame timestamps and save to file
    ff_str = ("'" + "movie =" + str(infile) + ",fps=fps=" + str(r) + "[out0]" + "'")
    os.system("ffprobe -f lavfi -i " + ff_str + " -show_frames -show_entries frame=pkt_pts_time -of csv=p=0 > frames.txt")
    os.system("paste images.txt frames.txt > combined.txt")
    
def get_creation_time(mov_file):
    
    
    #   Save video creation time to creation_time.txt
    os.system("ffprobe -v quiet -select_streams v:0  -show_entries stream_tags=creation_time -of default=noprint_wrappers=1:nokey=1 " + str(mov_file)+ " >creation_time.txt")
            
    c_time_file = open ("./creation_time.txt")
    c_time = c_time_file.read()
    c_time_dtobj = datetime.strptime(c_time[:-2].replace("T", " "), '%Y-%m-%d %H:%M:%S.%f')
    return(c_time_dtobj)

def get_gpx_time(gpx_filename):
    
    gpx_file = open(gpx_filename, 'r')
    gpx = gpxpy.parse(gpx_file)
    gpx_start_time = gpx.tracks[0].segments[0].points[0].time
    return(gpx_start_time)

def timestamp_images(img_list, mov_file):
     
    frame_list_file = open('frames.txt')
    frame_list = frame_list_file.readlines()
    
    creation_time = get_creation_time(mov_file)
    for i, filename in enumerate(image_list):
        
        exif_dict = pe.load(filename)
        
        
        new_date_dt = creation_time + timedelta(seconds = i)
        new_date = new_date_dt.strftime("%Y:%m:%d %H:%M:%S")
        
        exif_dict['0th'][pe.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][pe.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][pe.ExifIFD.DateTimeDigitized] = new_date
        exif_bytes = pe.dump(exif_dict)
        pe.insert(exif_bytes, filename)
    
r = 1 # The number of frames to extract per second. 

#   Get name of MP4 file to process from commandline argument
infile = sys.argv[1] 
filestem = os.path.splitext(infile)[0]
outfile = filestem 
run_gopro2gpx(infile, outfile)

extract_images(infile)

image_list_file = open("images.txt")
image_list = image_list_file.readlines()

for i, img in enumerate(image_list):
    image_list[i] = img[:-1]

mov_file = infile
timestamp_images(image_list, mov_file)

os.system("gpscorrelate -v -g ../GH010014.gpx  -z -8 ./extracted_images/*.jpeg")
