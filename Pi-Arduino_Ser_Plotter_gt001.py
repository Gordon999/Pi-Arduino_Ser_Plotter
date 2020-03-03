#! /usr/bin/env python3
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
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

if os.path.exists('/run/shm/example.txt'): # note log currently saved to RAM if log = 1
   os.remove('/run/shm/example.txt')       # gets deleted as you restart the script

if os.path.exists('/dev/ttyACM0'):
   ser = serial.Serial(port='/dev/ttyACM0',baudrate = 9600,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
elif os.path.exists('/dev/ttyACM1'):
   ser = serial.Serial(port='/dev/ttyACM1',baudrate = 9600,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
else:
   ser = serial.Serial(port='/dev/ttyUSB0',baudrate = 9600,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)


# set variables
global xs,y1,y2,y3,y4,y5,max_count,max_log, count,list_lock,start
max_count = 360
max_log = 86400
xlabel = "'click on the plot to stop on next update'"
ylabel = "dB"
plots = 5
count = 0
log = 0 # set log to 1 to save a log in RAM.
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

#kill the toolbar
plt.rcParams['toolbar'] = 'None'

# beautify

plt.style.use('seaborn-darkgrid')
plt.rc('figure', facecolor='darkgrey')
plt.rc('figure.subplot', left=0.06, right=0.99, top=0.99, bottom=0.08)
plt.rc('xtick', labelsize=6)     
plt.rc('ytick', labelsize=6)
plt.rc('lines', linewidth=1)
plt.rc('legend', frameon=True, loc='upper left', facecolor='white', framealpha=0.5, fontsize=7)
plt.rc('font', size=9)
plt.ioff()
      
def thread_plot():
    global fig,animate, ax1, intervl
    fig = plt.figure("Sound Pressure Level")
    ax1 = fig.add_subplot(1,1,1)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    ani = animation.FuncAnimation(fig, animate, interval=10000)
    plt.show()
   
def animate(i):
    global xs,y1,y2,y3,y4,y5,max_count,count,list_lock,start, plots, xlabel, ylabel
    if count > 0 and start == 1:
        ax1.clear()
        plt.xlabel(xlabel) 
        plt.ylabel(ylabel)
        ax1.xaxis.set_major_locator(MultipleLocator(30))
        ax1.xaxis.set_minor_locator(MultipleLocator(10))
        while list_lock == 1:             # wait if arrays being written to
            time.sleep(0.01)
        list_lock = 1                     # prevent arrays being written to
        ax1.plot(xs, y1, '-.b', label='Avg')
        if plots > 1:
            ax1.plot(xs, y2, '-r',  label='A0')
        if plots > 2:
            ax1.plot(xs, y3, '-g',  label='A0Slow')
        if plots > 3:
            ax1.plot(xs, y4, ':c',  label='Min')
        if plots > 4:
            ax1.plot(xs, y5, ':y',  label='Max')
        ax1.legend(loc='upper left')
        list_lock = 0                     # allow arrays to be written to
    if count > 0 and start == 0:
       plt.close('all')

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
    linetype = "#"                          # preset with error
    if counter1 == 0 and counter2 == 0 and counter3 == 0:     # waiting for sync
      linetype = "s"
    elif counter3 == 4  :                     # header line
      b,c,d,e,f = Ard_data.split(",")
      plots = int(b)
      max_count = int(c)
      log = int(d)
      xlabel = e
      ylabel = f[0:len(f)-2] 
      linetype = "h"    
    elif counter1 == 4 and counter2 == 5:     # valid data line
      b,c,d,e,f= Ard_data.split(" ")
      linetype = "d"
                                            # wait if animate using arrays
      while list_lock == 1:
          time.sleep(0.01)
      list_lock = 1                         # prevent animate using arrays
                                            # write to lists
      xs.append(t)
      y1.append(float(b))
      y2.append(float(c))
      y3.append(float(d))
      y4.append(float(e))
      y5.append(float(f))
                                            # delete old list values
      if len(xs) > max_count:
            del xs[0]
            del y1[0]
            del y2[0]
            del y3[0]
            del y4[0]
            del y5[0]
      list_lock = 0                        # release arrays for animate
      count +=1

    if log > 0:                           # save to log file  
      timestamp = now.strftime("%y/%m/%d-%H:%M:%S")
      with open('/run/shm/example.txt', 'a') as g:
         g.write(timestamp + " " + str(count)+" " + Ard_data +" "+ linetype)

    if linetype == "#":
       print("unexpected serial data, got that:[ " + Ard_data + "] please check")
  
  ser.close()
  sys.exit()
  
