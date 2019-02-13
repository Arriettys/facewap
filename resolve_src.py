#!/usr/bin/env python
#-*- coding:UTF-8 -*-

from subprocess import call
import os

if sys.version_info[0] < 3:
    raise Exception("This program requires at least python3.6")
if sys.version_info[0] == 3 and sys.version_info[1] < 6:
    raise Exception("This program requires at least python3.6")

ffmpeg = "./tools/ffmpeg-4.1-64bit-static/ffmpeg"
paramter = "-i"
video = "./workspace/data_src/video.mp4"
picture = "./workspace/data_src/picture"
command = [ffmpeg,paramter,video,picture + "/%d.png"]
if os.path.isdir(picture):
    call(["rm","-r"], shell=False)
call(["mkdir",picture], shell=False)
call(command, shell=False)
