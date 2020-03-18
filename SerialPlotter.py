#! /usr/bin/env python3

# getting libraries
import serial
import os, sys
import threading
import queue
import datetime
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

# configuration
serial_port = '/dev/ttyUSB0'
log = 1
log_path = '/home/pi/Noise/'
plot_tracks = 5    #not yet relevant...
plot_length = 360
page_length = 300  #only relevant for PolLog.py
plot_labels = ('Avg','A0','A0Slow','Min','Max')
plot_styles = ('-.b','-r','-g',':c',':y')
    #plot styles summary, any combination of line syle an color is allowed:
        # -  solid line
        # :  dotted line
        # -. dash-dotted line
        # r g b m c y k   for red, green blue, magenta, cyan, black

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

# kill the useless Matplotlib toolbar
plt.rcParams['toolbar'] = 'None'


def animate(i):
    global xs,y1,y2,y3,y4,y5,plot_length,count,list_lock,start
    if count > 0 and start == 1:
        ax1.clear()
        plt.xlabel('click on the plot to stop on next update') 
        plt.ylabel('dB')
        ax1.xaxis.set_major_locator(MultipleLocator(30))
        ax1.xaxis.set_minor_locator(MultipleLocator(10))
        while list_lock == 1:
             time.sleep(0.01)
        list_lock = 1
        ax1.plot(xs, y1, plot_styles[0], label = plot_labels[0] ) 
        ax1.plot(xs, y2, plot_styles[1], label = plot_labels[1] )
        ax1.plot(xs, y3, plot_styles[2], label = plot_labels[2] )
        ax1.plot(xs, y4, plot_styles[3], label = plot_labels[3] )
        ax1.plot(xs, y5, plot_styles[4], label = plot_labels[4] )
        ax1.legend(loc='upper left')
        list_lock = 0
    if count > 0 and start == 0:
       plt.close('all')
       
      
def thread_plot():
    global fig,animate, ax1
    fig = plt.figure("Sound Pressure Level from" + serial_port)
    ax1 = fig.add_subplot(1,1,1)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    ani = animation.FuncAnimation(fig, animate, interval=10000) #update every 10sec
    plt.show()

ser = serial.Serial(port= serial_port)
 
# set variables
global xs,y1,y2,y3,y4,y5,max_count,count,list_lock,start
max_count = 360
count = 0
xs = []
y1 = []
y2 = []
y3 = []
y4 = []
y5 = []
start = 1
list_lock = 0


def onclick(x):
   global start
   start = 0
      
def thread_plot():
    global fig,animate, ax1
    fig = plt.figure("Sound Pressure Level from" + serial_port)
    ax1 = fig.add_subplot(1,1,1)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    ani = animation.FuncAnimation(fig, animate, interval=10000) #update every 10sec
    plt.show()

if __name__ == '__main__':
   
  plot_thread = threading.Thread(target=thread_plot)
  plot_thread.start()

  while start == 1:                         #read serial data
    Ard_data = ser.readline()
    Ard_data = Ard_data.decode("utf-8","ignore")
    counter1 = Ard_data.count(' ')
    counter2 = Ard_data.count('.')
    counter3 = Ard_data.count(',')
    now = datetime.datetime.now()
    t = str(now)[11:19]                     # current time as hhmmss
                                            # check for linetype
    linetype = "#"                          # preset with error, should be overwitten next
    if counter1 == 0 and counter2 == 0 and counter3 == 0:     # waiting for sync
      linetype = "s"
    if counter3 == 4  :                     # header line
      b,c,d,e,f= Ard_data.split(",")
      linetype = "h"    
    if counter1 == 4 and counter2 == 5:     # valid data line
      b,c,d,e,f= Ard_data.split(" ")
      linetype = "d"
                                            # write to lists
      while list_lock == 1:
          time.sleep(0.01)
      list_lock = 1
      xs.append(t)
      y1.append(float(b))
      y2.append(float(c))
      y3.append(float(d))
      y4.append(float(e))
      y5.append(float(f))
      # delete old list values
      if len(xs) > plot_length:
            del xs[0]
            del y1[0]
            del y2[0]
            del y3[0]
            del y4[0]
            del y5[0]
      list_lock = 0
      count +=1
      
    if log == 1:                          # save to log file  
      timestamp = now.strftime("%H:%M:%S")
      hour = datetime.datetime.now()
      hourago = hour - datetime.timedelta(hours = 1)  # new file starts at 01:00
      logfile = log_path + hourago.strftime("%y-%m-%d") +'.log'
      if (os.path.exists(logfile)): 
         pass
      else :                                          # logfile does not exist, jettison a new one
         print ('new', logfile, 'is starting')         
      with open(logfile, 'a') as g:
         g.write(linetype  + " " + timestamp + " " + Ard_data)
    if linetype == "#":
       print("unexpected serial data, got that:[ " + Ard_data + "] please check")
  
  ser.close()
  sys.exit()
