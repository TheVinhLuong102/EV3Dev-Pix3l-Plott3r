#!/usr/bin/python
# -*- coding: utf-8 -*- import python packages

#install --> (sudo) apt-get install python-pip --> (sudo) pip install pillow python-ev3dev
#running --> run (sudo) python pythonfilename.py imagefilename.png (jpg will work along with others types) -->
#            you will be given a dialogue --> just type "" and return/enter to continue

from PIL import Image, ImageFilter
import ev3dev.ev3 as ev3
import time
from ev3dev import *
import os
import sys

# paper resolution
horiz_deg = -1800; #degress max move
horiz_width = 5; #inches
horiz_res = horiz_deg/horiz_width; # degrees per inch
vertical_deg = 850; #degress max move
vertical_width = 6.5; #inches
vertical_res = vertical_deg/vertical_width; # degrees per inch
vert_move = 7;
horiz_move = vert_move*horiz_res/vertical_res;
res = horiz_deg/horiz_move/1.1;

#function to ensure the motor has stopped before moving on
xxx = 0
def waitformotor(motor):
    #run more than once to ensure that motor is stopped and that it was not a false reading
    while motor.state == [u'running'] or motor.state == [u'ramping']:
        xxx = 0
    while motor.state == [u'running'] or motor.state == [u'ramping']:
        xxx = 0
    while motor.state == [u'running'] or motor.state == [u'ramping']:
        xxx = 0
    while motor.state == [u'running'] or motor.state == [u'ramping']:
        xxx = 0


# define motors and use brake mode
col = ev3.ColorSensor()
paper = ev3.MediumMotor('outA')
pen = ev3.LargeMotor('outB')
LR = ev3.MediumMotor('outC')
pen.stop_command = u"brake"
LR.stop_command = u"brake"
paper.stop_command = u"brake"
LR.ramp_up_sp=100
LR.ramp_down_sp=200
LR.reset()
LR.run_to_abs_pos(position_sp=-50, duty_cycle_sp=75)
waitformotor(LR)
waitformotor(LR)
LR.reset()
LR.speed_regulation_enabled=u'on'

#move paper until color sensor recieves >50 reading
while col.value() < 50:
    paper.run_forever(duty_cycle_sp=40)
paper.stop()
paper.reset()

paper.speed_regulation_enabled=u'on'



#make a function to make a dot on the page
def makedot():
    pen.run_timed(time_sp=250, duty_cycle_sp=-75)
    waitformotor(pen)
    waitformotor(pen) #double check if motor is stopped before raising pen
    pen.run_timed(time_sp=100, duty_cycle_sp=75)
    waitformotor(pen)
    waitformotor(pen)


#resise and flip image
filename = sys.argv[1]
cmd = "convert " + filename + " -threshold 90% -flop -resize " + str(res) + " print.jpg"
os.system(cmd) #execute command
image_file = Image.open('print.jpg') # open image print.jpg in current directory
image_file = image_file.convert('1') # convert image to pure black and white (just in case image is greyscale or color)
image_file.save('print.png') # save b&w image

w = 0
h = 0
l = 0
img = Image.open('print.png') #open black and white image
width, height = img.size # get image size
array = []
print width," x ", height
while h != height:
        while w != width:
                array.append(img.getpixel((w, h))) #get black or white of each pixel
                w = w+1 #move to next pixel
        w = 0 #reset width counter
        h = h+1 #move to next row

all_pixels = array #save array of pixels to all_pixels

x = input('Type text to preview picture (in quotes) >>') #wait until dialogue is answered then show preview

width, height = img.size #get image size
xd = 0
yd = 0
xda = 0
while yd != height:
    while xd != width:
        if all_pixels[xda] == 0: #is pixel black?
            print "█", #print block if black pixel
        else:
            print " ",
        xd = xd + 1
        xda = xda + 1
    print(" ")
    yd = yd + 1
    xd = 0

x = input('Is this picture ok? If not pres ctrl-c >>') #wait for dialogue to be answered then start printing

xd = 0
yd = 0
xda = 0
while yd != height:
    while xd != width:
        if all_pixels[xda] == 0: #is pixel black?
            print "█", #print block if black pixel
            # lower and raise pen
            pen.run_timed(time_sp=250, duty_cycle_sp=-75)
            makedot()
            # move pen left
            LR.run_to_abs_pos(position_sp=horiz_move*xd, speed_sp=400, ramp_down_sp=500)
            waitformotor(LR)
        else:
            print " ",
            #move pen left
            LR.run_to_abs_pos(position_sp=horiz_move*xd, speed_sp=400, ramp_down_sp=500)
            waitformotor(LR)
        xd = xd + 1
        xda = xda + 1

    print(" ")
    yd = yd + 1
    xd = 0
    # move paper forward
    paper.run_to_abs_pos(position_sp=vert_move*(yd), speed_sp=250,ramp_down_sp=500)
    # reset pen location
    LR.run_to_abs_pos(position_sp=0, duty_cycle_sp=75)
    waitformotor(paper)
    waitformotor(paper)
    waitformotor(LR)
    waitformotor(LR)

paper.run_timed(time_sp=5000, duty_cycle_sp=75) #eject paper
time.sleep(5)
LR.run_to_abs_pos(position_sp=50, duty_cycle_sp=75) #reset to original position
time.sleep(2)
