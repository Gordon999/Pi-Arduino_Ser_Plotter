#! /usr/bin/env python3

# getting libraries
import os
import subprocess
import threading
import time
import tkinter as tk
import datetime
from datetime import datetime as DateTime, timedelta as TimeDelta
from tkinter import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import (MultipleLocator)
from tkcalendar import DateEntry

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
        self.list_lock = 0
        self.s_plot = 0
        self.legend = 1

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

        # setup tkinter window
        Frame10 = tk.Frame(width=300, height=60)
        Frame10.grid_propagate(0)
        Frame10.grid(row=0, column=0)
        Frame11 = tk.Frame(width=300, height=60)
        Frame11.grid_propagate(0)
        Frame11.grid(row=2, column=0)
        button2 = tk.Button(Frame10, text="Exit", command=self.exit, bg = "red")
        button2.grid(row = 0, column = 3, padx = 0)
        button = tk.Button(Frame10, text="Plot", command=self.Plot, bg = "green", fg = "white")
        button.grid(row = 0, column = 0)
        self.in_date = DateEntry(Frame10, width=8, borderwidth=2,date_pattern = "yy-m-d",state="readonly")
        self.in_date.grid(row = 1, column = 1, padx = 30)
        self.mhourstr=tk.StringVar(self,'13')
        self.mhour = tk.Spinbox(Frame11,from_=0,to=23,wrap=True,textvariable=self.mhourstr,width=2,state="readonly")
        self.mminstr=tk.StringVar(self,'00')
        self.mminstr.trace("w",self.mtrace_var_m)
        self.mlast_value_m = ""
        self.mmin = tk.Spinbox(Frame11,from_=0,to=59,wrap=True,textvariable=self.mminstr,width=2,state="readonly")
        self.msecstr=tk.StringVar(self,'00')
        self.msecstr.trace("w",self.mtrace_var_s)
        self.mlast_value_s = ""
        self.msec = tk.Spinbox(Frame11,from_=0,to=59,wrap=True,textvariable=self.msecstr,width=2,state="readonly")
        self.mhour.grid(row=4,column=1)
        self.mmin.grid(row=4,column=2)
        self.msec.grid(row=4,column=3)
        L1 = tk.Label(Frame10, text="      Date :" , font = 20)
        L1.grid(row=1, column = 0)
        L2 = tk.Label(Frame11, text="Mid Time :" , font = 20)
        L2.grid(row=4, column = 0)
        self.L4 = tk.Label(Frame10, text="" , font = 20)
        self.L4.place(x=230, y=30)
        
    # check for hour increment if mins > 59
    def mtrace_var_m(self,*args):
        if self.mlast_value_m == "59" and self.mminstr.get() == "0":
            self.mhourstr.set(int(self.mhourstr.get())+1 if self.mhourstr.get() !="23" else 0)
        self.mlast_value_m = self.mminstr.get()
    # check for min increment if secs > 59
    def mtrace_var_s(self,*args):
        if self.mlast_value_s == "59" and self.msecstr.get() == "0":
            self.mminstr.set(int(self.mminstr.get())+1 if self.mminstr.get() !="59" else 0)
        self.mlast_value_s = self.msecstr.get()

    def exit(self):
        self.start = 0
        self.master.destroy()
        
    def click(self,event):
        # RIGHT click (NEXT)
        if event.button == 3:
            self.mid_count += self.plot_length - 1
            self.mid_time3 = str(datetime.datetime.strptime(self.mid_time3,'%H:%M:%S') + TimeDelta(seconds=self.plot_length))[11:19]
            self.legend = 1
            if self.mid_count + int(self.plot_length/2) > self.count_x:
                self.mid_count = self.count_x - int(self.plot_length/2)
                self.mid_time3 = str(datetime.datetime.strptime(self.mid_time3,'%H:%M:%S') - TimeDelta(seconds=self.plot_length))[11:19]
                self.legend = 2
            self.read_plot()
        # LEFT click (PREVIOUS)
        elif event.button == 1 :
            self.mid_count -= self.plot_length -1
            self.mid_time3 = str(datetime.datetime.strptime(self.mid_time3,'%H:%M:%S') - TimeDelta(seconds=self.plot_length))[11:19]
            self.legend = 1
            if self.mid_count < int(self.plot_length/2) + 1:
                self.mid_count = int(self.plot_length/2) + 1
                self.mid_time3 = str(datetime.datetime.strptime(self.mid_time3,'%H:%M:%S') + TimeDelta(seconds=self.plot_length))[11:19]
                self.legend = 0
            self.read_plot()

    def Plot(self):
        # clear NO LOG comment, if present
        self.L4.config(text= "      ")
        # ensure in_date is in the correct format to match the log data
        dat = datetime.datetime.strptime(self.in_date.get(), '%y-%m-%d').strftime('%y-%m-%d')
        mtim = self.mhour.get() + ":" +  self.mmin.get() + ":" +  self.msec.get()
        # ensure mid_time is in the correct format to match the log data
        self.mid_time = datetime.datetime.strptime(mtim, '%H:%M:%S').strftime('%H:%M:%S')
        # stop animation
        self.start = 0
        # set mid_count to 0, forcing log file to be read.
        self.mid_count = 0
        self.log_file = self.log_path + dat + ".log"
        self.read_plot()
    
    def thread_plot(self):
        self.fig = plt.figure("Sound Pressure Level")
        self.ax1 = self.fig.add_subplot(1,1,1)
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.click)
        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=100) 
        plt.show()
   
    def animate(self, i):
        if self.count > 0 and self.start == 1:
            self.ax1.clear()
            if self.legend == 1:
                plt.xlabel('Mid Time: ' + self.mid_time3 + ' Log: ' + self.log_file[len(self.log_path):] + " - LEFT for PREVIOUS, RIGHT for NEXT")
            elif self.legend == 0:
                plt.xlabel('Mid Time: ' + self.mid_time3 + ' Log: ' + self.log_file[len(self.log_path):] + " - RIGHT for NEXT")
            elif self.legend == 2:
                plt.xlabel('Mid Time: ' + self.mid_time3 + ' Log: ' + self.log_file[len(self.log_path):] + " - LEFT for PREVIOUS") 
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
        if os.path.exists (self.log_file):
            self.xs = []
            self.y1 = []
            self.y2 = []
            self.y3 = []
            self.y4 = []
            self.y5 = []
            self.start = 1

            # start animation (only once)
            if self.count == 0:
                self.mid_time3 = self.mid_time
                plot_thread = threading.Thread(target=self.thread_plot)
                plot_thread.start()
                self.count = 1
            if self.count == 1:        
                # delete temporary filtered log
                if os.path.exists('/run/shm/plot.log'): 
                    os.remove('/run/shm/plot.log')
             
                # generate temporary filtered log
                # check if mid_count = 0, only run once when plot pressed.
                if self.mid_count == 0:
                    objFile = open(self.log_file, "r")
                    self.count_x = 0
                    s_count = 0
                    e_count = 0
                    for line in objFile:
                        if self.mid_time in line:
                                self.mid_count = self.count_x
                                self.mid_time3 = self.mid_time
                        self.count_x += 1       
                    objFile.close()
                    
                    # if no required mid_time entry are found then increment time by 1 second, 3 times.
                    if self.mid_count == 0:
                        objFile = open(self.log_file, "r")
                        self.mid_time2 = self.mid_time
                        self.count_y = 0
                        stop = 0
                        for dev in range(1,4):
                            self.mid_time = str(datetime.datetime.strptime(self.mid_time2,'%H:%M:%S') + TimeDelta(seconds=dev))[11:19]
                            self.count_y = 0
                            for line in objFile:
                                if self.mid_time in line and stop == 0:
                                    self.mid_count = self.count_y
                                    self.mid_time3 = self.mid_time
                                    stop = 1
                                self.count_y += 1
                        objFile.close()
                        
                # calculate start_count and end_count from mid_count and plot_length
                start_count = self.mid_count - int(self.plot_length/2)
                end_count = self.mid_count + int(self.plot_length/2)
                # ensure not exceeding the ends of the log
                if start_count < 1:
                    start_count = 1
                    end_count = start_count + self.plot_length
                    self.mid_time3 = str(datetime.datetime.strptime("00:00:00",'%H:%M:%S') + TimeDelta(seconds=int(self.plot_length/2)))[11:19]
                elif end_count > self.count_x:
                    end_count = self.count_x
                    start_count = end_count - self.plot_length
                    self.mid_time3 = str(datetime.datetime.strptime("23:59:59",'%H:%M:%S') - TimeDelta(seconds=int(self.plot_length/2)))[11:19]
                # call subrocess for temp log
                path = "sed -n " +  str(start_count)  + "," +  str(end_count) + "p " + '"' + self.log_file + '"' + " >> /run/shm/plot.log"
                p = subprocess.Popen(path, shell=True, preexec_fn=os.setsid)
                # wait while temp log generated
                poll = p.poll()
                while poll == None:
                    time.sleep(.01)
                    poll = p.poll()
               #read temporary filtered log
                self.log= []
                with open("/run/shm/plot.log", "r") as file:
                    line = file.readline()
                    # check for a valid line
                    if line[0:1] == "d":
                        counter1 = line.count(' ')
                        counter2 = line.count('.')
                        if counter1 == 6 and counter2 == 5:
                            self.log.append(line)
                    self.stop = 1
                    while line and self.stop:
                        line = file.readline()
                        self.log.append(line)
            # put values in lists for plotting
            if len(self.log) >= self.plot_length:
                for x in range(0,self.plot_length):
                    if self.log[x][0:1] == "d":
                        counter1 = self.log[x].count(' ')
                        counter2 = self.log[x].count('.')
                        if counter1 == 6 and counter2 == 5:
                            a,t,b,c,d,e,f = self.log[x].split(" ")
                            self.xs.append(t)
                            self.y1.append(float(b))
                            self.y2.append(float(c))
                            self.y3.append(float(d))
                            self.y4.append(float(e))
                            self.y5.append(float(f))
        else:
            # no log found for date entered
            self.L4.config(text= "No log")

          
def main():
    root = Tk()
    root.title("Choose a log...")
    ex = Plot()
    root.mainloop() 

if __name__ == '__main__':
    main()  
