#! /usr/bin/env python3

# getting libraries
import serial
import os, sys
import threading
import queue
import datetime
import time
import glob
import tkinter as tk
from tkinter import *
from tkinter import ttk
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

class Plot(Frame):
    def __init__(self):
        super().__init__() 
        self.initUI()

    def initUI(self):
        # configuration
        self.plot_length = 360
        self.log_path = '/home/pi/Noise/'
        
        # set variables
        self.count = 0
        self.xs = []
        self.y1 = []
        self.y2 = []
        self.y3 = []
        self.y4 = []
        self.y5 = []
        self.start = 1
        self.go = 1
        self.list_lock = 0

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


        Frame10 = tk.Frame(width=300, height=70)
        Frame10.grid_propagate(0)
        Frame10.grid(row=0, column=0)
        button2 = tk.Button(Frame10, text="exit", command=self.exit, bg = "red")
        button2.grid(row = 0, column = 2)
        button = tk.Button(Frame10, text="Plot", command=self.Plot, bg = "green", fg = "white")
        button.grid(row = 0, column = 0)
        OPTIONS = glob.glob(self.log_path + '*.log')
        self.variable = StringVar(Frame10)
        self.variable.set(OPTIONS[0])
        w = OptionMenu(Frame10, self.variable, *OPTIONS)
        w.grid(row = 1, column = 0, columnspan = 3)

    def exit(self):
        self.start = 0
        self.master.destroy()
        
    def exit2(self,x):
        self.start = 0
        self.master.destroy()

    def Plot(self):
        self.start = 0
        self.log_file = self.variable.get()
        self.read_plot()
    
    def thread_plot(self):
        self.fig = plt.figure("Sound Pressure Level")
        self.ax1 = self.fig.add_subplot(1,1,1)
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.exit2)
        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=1000) #update every 1 sec
        plt.show()
   
    def animate(self,i):
        if self.count > 0 and self.start == 1:
          self.ax1.clear()
          plt.xlabel('Log: ' + self.log_file + '     -     click on the plot to exit') 
          plt.ylabel('dB')
          self.ax1.xaxis.set_major_locator(MultipleLocator(30))
          self.ax1.xaxis.set_minor_locator(MultipleLocator(10))
          while self.list_lock == 1:
             time.sleep(0.01)
          self.list_lock = 1
          self.ax1.plot(self.xs, self.y1, '-.b', label='Avg')     # dash-dotted line, blue
          self.ax1.plot(self.xs, self.y2, '-r',  label='A0')      # solid line, red
          self.ax1.plot(self.xs, self.y3, '-g',  label='A0Slow')  # solid line, green
          self.ax1.plot(self.xs, self.y4, ':c',  label='Min')     # dotted line, cyan
          self.ax1.plot(self.xs, self.y5, ':y',  label='Max')     # dotted line, yellow
          self.ax1.legend(loc='upper left')
          self.list_lock = 0
        if self.count > 0 and self.start == 0 :
            plt.close('all')
          

    def read_plot(self):
     self.xs = []
     self.y1 = []
     self.y2 = []
     self.y3 = []
     self.y4 = []
     self.y5 = []
     self.start = 1
     self.go = 1

     if self.count == 0:
        plot_thread = threading.Thread(target=self.thread_plot)
        plot_thread.start()
     self.count = 1
     while self.go == 1:
          #read log
          log= []
          with open(self.log_file, "r") as file:
              line = file.readline()
              log.append(line)
              while line:
                  line = file.readline()
                  log.append(line)
                  
          for x in range(0,len(log)):
              # set read delay
              time.sleep(.01)
              # check for data lines
              if log[x][0:1] == "d":
                  counter1 = log[x].count(' ')
                  counter2 = log[x].count('.')
                  if counter1 == 6 and counter2 == 5:     # valid data line
                      x,t,b,c,d,e,f= log[x].split(" ")
                      while self.list_lock == 1:
                          time.sleep(0.01)
                      self.list_lock = 1
                      self.xs.append(t)
                      self.y1.append(float(b))
                      self.y2.append(float(c))
                      self.y3.append(float(d))
                      self.y4.append(float(e))
                      self.y5.append(float(f))
                      # delete old list values
                      if len(self.xs) > self.plot_length:
                          del self.xs[0]
                          del self.y1[0]
                          del self.y2[0]
                          del self.y3[0]
                          del self.y4[0]
                          del self.y5[0]
                      self.list_lock = 0
 
          self.go = 0
          
def main():
    root = Tk()
    root.title("Choose a log...")
    ex = Plot()
    root.geometry("300x70")
    root.mainloop() 

if __name__ == '__main__':
    main() 
