import os
from shutil import rmtree
import bs4
import subprocess
import webbrowser
import time
import numpy as np

# TODO make this work with windows as well

# Killing the servers if they are open (if the script was run before, this script )
os.system('killall -KILL node')

# Remove the distrubution file if it was created before
if os.path.isdir('dist'):    
    rmtree('dist')

# Read the generic html script for overriding
with open('posenet/demos/videoTemplate.html') as inf:
    txt = inf.read()
    soup = bs4.BeautifulSoup(txt) # Used to edit html files

base_path = os.getcwd()

# Create the directory for storing video frames
if not os.path.isdir(os.path.join(base_path,'temp')):
    os.mkdir(os.path.join(base_path,'temp'))
else:
    rmtree(os.path.join(base_path,'temp'))
    os.mkdir(os.path.join(base_path,'temp'))

# Separate the input video into individual frames
command = "ffmpeg -i  vid.mp4 -b:v 100M " + os.path.join(base_path,'temp','in%d.jpg')
os.system(command)
# At this point, video is turned into images in /temp file

# how many frames there is in the input video
frames = len([f for f in os.listdir(base_path+'/temp') if f.startswith('in') ])

# Every frame that was ing the video was added to the html script as a new tag
for i in range(frames):
    new_link = soup.new_tag("img", id="input"+str(i+1), src=os.path.join('temp','in'+str(i+1)+'.jpg'), style='display:none')
    soup.head.append(new_link)

# A new html file will be created (or overwritten) to be used by posenet
tabname = 'video.html'
with open(tabname, "w") as outf:
    outf.write(str(soup.prettify()))

# Opening a dev server on localhost:1234
command1 = subprocess.Popen(['yarn', 'watch'])

time.sleep(6) # Wait till it was built

webbrowser.open_new_tab('localhost:1234/'+tabname) # Open the tab in which the posenet will be run for the video

# If you want to download the keypoint detection data as a .json file, enable it on the 
# video.js script
