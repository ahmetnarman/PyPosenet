"""
This is a script that allows using posenet on a browser and getting keypoints for the pose estimation pipeline.
The code is really hacky and it may not be the most efficient way of doing it but I tried to make it the
best I could. If you are going to use this code, sorry in advance.

Cheers,

Ahmet
"""

import os
from shutil import rmtree
import bs4
import subprocess
import webbrowser
import time
import json
import numpy as np

def runPosenet(vid_path, model):

    # Killing the servers if they are open
    os.system('killall -KILL node')

    # Read the generic html script for overriding
    with open('posenet/demos/video.html') as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt) # Used to edit html files

    base_path = "/home/a/project/videos/"

    # Create the directory for intermediate images
    if not os.path.isdir(base_path +"/temp"):
        os.mkdir(base_path+"/temp")
    else:
        rmtree(base_path + '/temp')
        os.mkdir(base_path + "/temp")

    # Separate the input video into individual frames
    command = "ffmpeg -i " + vid_path + " -b:v 100M " + base_path + "/temp/in%d.jpg"
    os.system(command)
    # At this point, video is turned into images in /temp file

    # how many frames there is in the input video
    frames = len([f for f in os.listdir(base_path+'/temp') if f.startswith('in') ])

    for i in range(frames):
        new_link = soup.new_tag("img", id="input"+str(i+1), src='../../videos/temp/in'+str(i+1)+'.jpg', style='display:none')
        soup.head.append(new_link)

    cwd = os.getcwd()
    os.chdir('/home/a/project/posenet/demos/')
    print(soup.prettify())

    tabname = ''

    if model == 'mobile_fast':
        tabname = 'video_M1.html'
        with open(tabname, "w") as outf:
            outf.write(str(soup.prettify()))
    elif model =='mobile_slow':
        tabname = 'video_M2.html'
        with open(tabname, "w") as outf:
            outf.write(str(soup.prettify()))
    elif model == 'resnet_fast':
        tabname = 'video_R1.html'
        with open(tabname, "w") as outf:
            outf.write(str(soup.prettify()))
    elif model == 'resnet_slow':
        tabname = 'video_R2.html'
        with open(tabname, "w") as outf:
            outf.write(str(soup.prettify()))
    else:
        raise Exception("The specified keypoint detector model doesn't exist")

    command1 = subprocess.Popen(['yarn', 'watch'])

    time.sleep(6)

    webbrowser.open_new_tab('localhost:1234/'+tabname)

    print('Waiting for the keypoint data')
    while not os.path.exists('/home/a/Downloads/json.txt'):
        time.sleep(1)

    if os.path.isfile('/home/a/Downloads/json.txt'):
        json_data = json.load(open('/home/a/Downloads/json.txt'))
    else:
        raise ValueError("%s isn't a file!" % '/home/a/Downloads/json.txt')

    assert frames == len(json_data)

    keypoints = np.zeros((len(json_data),17,2))

    coords = ['x', 'y']

    for i in range(frames):
        for j in range(17):
            for c in range(len(coords)):
                keypoints[i,j,c] = json_data[i]['keypoints'][j]['position'][coords[c]]

    print(keypoints.shape)

    # Wait for the file to be returned before running these two commands
    os.remove('/home/a/Downloads/json.txt')
    rmtree('dist')
    os.system('killall -KILL node')

    os.chdir(cwd)

    return keypoints