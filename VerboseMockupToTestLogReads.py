#! /usr/bin/env python3

# getting libraries
import os
import subprocess
import time
from datetime import datetime as DateTime, timedelta as TimeDelta
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import (MultipleLocator)
"""

# configuration
plot_length = 360                     # seconds > 6 minutes by page
log_path = '/home/pi/Noise/'
plot_path = '/run/shm/'
plot_file = 'plot.log'
presistence_file = 'persistence.dat'  # will be implemented later to keep input data

# source defaults
log_date_str = '20-03-10'             #logdate as string
log_mid_time_str = '23:50:00'         #logstarttime as string

"""                                   #not yet used, will soon be required.
# beautifying plot params
plt.style.use('seaborn-darkgrid')
plt.rc('figure', facecolor='darkgrey')
plt.rc('figure.subplot', left=0.06, right=0.99, top=0.99, bottom=0.08)
plt.rc('xtick', labelsize=6)     
plt.rc('ytick', labelsize=6)
plt.rc('lines', linewidth=1)
plt.rc('legend', frameon=True, loc='upper left', facecolor='white', framealpha=0.5, fontsize=7)
plt.rc('font', size=9)
plt.ioff()
#kill the useless Matplotlib toolbar
plt.rcParams['toolbar'] = 'None'

def labels_plot(self, i):
    if self.count > 0 and self.start == 1:
        self.ax1.clear()
        plt.xlabel('Log: ' + self.log_file + " - Clicks: LEFT for PREVIOUS, RIGHT for NEXT") 
        plt.ylabel('dB')
        self.ax1.xaxis.set_major_locator(MultipleLocator(30))
        self.ax1.xaxis.set_minor_locator(MultipleLocator(10))
        self.list_lock = 1
        self.ax1.plot(self.xs, self.y1, '-.b', label='Avg')     # dash-dotted line, blue
        self.ax1.plot(self.xs, self.y2, '-r',  label='A0')      # solid line, red
        self.ax1.plot(self.xs, self.y3, '-g',  label='A0Slow')  # solid line, green
        self.ax1.plot(self.xs, self.y4, ':c',  label='Min')     # dotted line, cyan
        self.ax1.plot(self.xs, self.y5, ':y',  label='Max')     # dotted line, yellow
        self.ax1.legend(loc='upper left')

def canvas_plot(self):
    self.fig = plt.figure("Sound Pressure Level")
    self.ax1 = self.fig.add_subplot(1,1,1)
    self.cid = self.fig.canvas.mpl_connect('button_press_event', self.exit2)
        #self.ani = animation.FuncAnimation(self.fig, self.animate, interval=1000) #update every 1 sec
    plt.show()

def on_mouse(self,event):
    # RIGHT click (NEXT screen)
    if event.button == 3:
        self.go = True
        self.s_plot += self.plot_length
        if self.s_plot > len(self.log) -1 - plot_length :
            self.s_plot = len(self.log) - 1 - plot_length
        self.read_plot()
    # LEFT click (PREVIOUS screen)
    elif event.button == 1 :
        self.go = True
        self.s_plot -= self.plot_length
        if self.s_plot < 0:
            self.s_plot = 0
        self.read_plot()

# set variables
count = 0
xs = [str]
y1 = [str]
y2 = [str]
y3 = [str]
y4 = [str]
y5 = [str]
start = True
pause = False
"""

# starting dialog
print ('Welcome to LogPlot')
print (f'This script reads and plots logfiles named yy-mm-dd.log located in folder {log_path}')
print (f'Defaults are  {log_path + log_date_str} .log, centered around {log_mid_time_str}')
answer = 'n'
answer = input ('taking that? n/y:')
if answer == 'y':
    get_data = True
else:
    get_data = False
# gathering date    
while not get_data:
    log_date_str = input ('Please enter log date (yy-mm-dd) :')
    #t.b.d: validate log_date_str syntactically, if wrong message + break, else
    log_file = log_path + log_date_str + '.log'
    print ('Searching for '+log_file)
    if os.path.exists(log_file):
        print(f'Reading data from file: {log_file}')
        get_data = True
    else:
        print(f'Sorry, {log_file} does not exist, try again')
        get_data = False
get_data = False
if answer == 'y':
    get_data = True
while not get_data:
    log_mid_time_str = input ('Please enter log centre time (hh:mm:ss) :')
    #t.b.d: validate log_time syntactically, if wrong message syntax , else
    get_data = True

log_mid_time = DateTime.strptime(log_mid_time_str, '%H:%M:%S')
log_stop_time = log_mid_time + TimeDelta(minutes=3)
log_start_time = log_mid_time + TimeDelta(minutes=-3)
log_file = log_path + log_date_str + '.log'
log_start_time_str = log_start_time.strftime('%H:%M:%S')
log_stop_time_str = log_stop_time.strftime('%H:%M:%S')
print (f'Using log start time {log_start_time_str}, log mid time {log_mid_time_str}, log end time {log_stop_time_str} in {log_file} .')
print ('Looking what we can get from that...')

"""                  #code that does not yet run
current_line = 0
start_line = 0
mid_line = 0
start_line = 0
millis0 = int(round(time.time() * 1000))
print ('starting chrono...')
with open(log_file, "r") as log_read:
    line = log_read.readline()
    #log_read.append(line)
    while line:
        if log_start_time_str in line:
            print (f'Found start timestamp @: {current_line}')
            start_line = current_line
        if log_mid_time_str in line:
            print (f'Found centre timestamp @: {current_line}')
            mid_line = current_line
        if log_stop_time_str in line:
            print (f'Found end timestamp @: {current_line}')
            stop_line = current_line
            break
        current_line += 1
"""                     #deprecated code, that works
log_read = open(log_file, 'r')
current_line = 0
start_line = 0
mid_line = 0
start_line = 0
millis0 = int(round(time.time() * 1000))
print ('starting chrono...')
found_start = False
found_stop= False
for line in log_read:
    """
    if log_start_time_str in line:
        print (f'Found start timestamp @: {current_line}')
        start_line = current_line
    if log_mid_time_str in line:
        print (f'Found centre timestamp @: {current_line}')
        mid_line = current_line
    if log_stop_time_str in line:
        print (f'Found end timestamp @: {current_line}')
        stop_line = current_line
        break
    """
    if line[0:1] == "d":
        log_line_time_str = line[2:9]
        log_line_time = DateTime.strptime(log_line_time_str, '%H:%M:%S')
        if log_line_time >= log_start_time and not found_start:
            start_line = current_line
            found_start = True
        elif log_line_time <= log_stop_time and not found_stop:
            stop_line = current_line
            found_stop = True
    current_line += 1
log_read.close()
mid_line = stop_line - start_line / 2

"""
if mid_line != '0':
    start_line = mid_line - 180
    stop_line = mid_line +180
elif start_line != '0':
    stop_line = start_line +360
    mid_line = start_line +180
elif stop_line != '0':
    start_line = stop_line -360
    mid_line = stop_line -180
else:
    print ('Sorry, no match found, try another time?')
"""    

millis = int(round(time.time() * 1000))
print (f'{millis - millis0} ms')
print (f'Start line = {start_line}, Mid Line = {mid_line}, End line = {stop_line} . Generating plot.log...')
# Copying 360 lines from the log file into the plot file
path = "sed -n " +  str(start_line)  + "," +  str(stop_line) + "p " + '"' + log_file + '"' + " >> /run/shm/plot.log"
p = subprocess.Popen(path, shell=True, preexec_fn=os.setsid)
millis = int(round(time.time() * 1000))
print (f'{millis - millis0} ms')
print ('Done!')
