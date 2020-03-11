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
plot_length = 360
log_path = '/home/pi/Noise/'
log_file = '20-03-08.log'

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
 
# set variables
count = 0
xs = []
y1 = []
y2 = []
y3 = []
y4 = []
y5 = []
start = 1
go = 1
list_lock = 0

def onclick(x):
   global start
   start = 0
      
def thread_plot():
    global fig,animate, ax1
    fig = plt.figure("Sound Pressure Level from " + log_file)
    ax1 = fig.add_subplot(1,1,1)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    ani = animation.FuncAnimation(fig, animate, interval=1000) #update every 1 sec
    plt.show()
   
def animate(i):
    global xs,y1,y2,y3,y4,y5,plot_length,count,list_lock,start
    if count > 0 and start == 1:
        ax1.clear()
        plt.xlabel('click on the plot to stop') 
        plt.ylabel('dB')
        ax1.xaxis.set_major_locator(MultipleLocator(30))
        ax1.xaxis.set_minor_locator(MultipleLocator(10))
        while list_lock == 1:
             time.sleep(0.01)
        list_lock = 1
        ax1.plot(xs, y1, '-.b', label='Avg')     # dash-dotted line, blue
        ax1.plot(xs, y2, '-r',  label='A0')      # solid line, red
        ax1.plot(xs, y3, '-g',  label='A0Slow')  # solid line, green
        ax1.plot(xs, y4, ':c',  label='Min')     # dotted line, cyan
        ax1.plot(xs, y5, ':y',  label='Max')     # dotted line, yellow
        ax1.legend(loc='upper left')
        list_lock = 0
    if count > 0 and start == 0:
        plt.close('all')

if __name__ == '__main__':
   
  plot_thread = threading.Thread(target=thread_plot)
  plot_thread.start()

  while start == 1:
      while go == 1:
          count +=1
          #read log
          log= []
          with open(log_path + log_file, "r") as file:
              line = file.readline()
              log.append(line)
              while line:
                  line = file.readline()
                  log.append(line)
                  
          for x in range(0,len(log)):
              # set read delay
              time.sleep(1)
              # check for data lines
              if log[x][0:1] == "d":
                  counter1 = log[x].count(' ')
                  counter2 = log[x].count('.')
                  if counter1 == 6 and counter2 == 5:     # valid data line
                      x,t,b,c,d,e,f= log[x].split(" ")
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
 
          go = 0


