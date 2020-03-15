#! /usr/bin/env python3

# getting libraries
import os
import subprocess
import threading
import time
import tkinter as tk
import datetime
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
        self.legend = 0

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
        self.shourstr=tk.StringVar(self,'13')
        self.shour = tk.Spinbox(Frame11,from_=0,to=23,wrap=True,textvariable=self.shourstr,width=2,state="readonly")
        self.sminstr=tk.StringVar(self,'00')
        self.sminstr.trace("w",self.strace_var_m)
        self.slast_value_m = ""
        self.smin = tk.Spinbox(Frame11,from_=0,to=59,wrap=True,textvariable=self.sminstr,width=2,state="readonly")
        self.ssecstr=tk.StringVar(self,'00')
        self.ssecstr.trace("w",self.strace_var_s)
        self.slast_value_s = ""
        self.ssec = tk.Spinbox(Frame11,from_=0,to=59,wrap=True,textvariable=self.ssecstr,width=2,state="readonly")
        self.shour.grid(row=4,column=1)
        self.smin.grid(row=4,column=2)
        self.ssec.grid(row=4,column=3)
        
        self.ehourstr=tk.StringVar(self,'13')
        self.ehour = tk.Spinbox(Frame11,from_=0,to=23,wrap=True,textvariable=self.ehourstr,width=2,state="readonly")
        self.eminstr=tk.StringVar(self,'15')
        self.eminstr.trace("w",self.etrace_var_m)
        self.elast_value_m = ""
        self.emin = tk.Spinbox(Frame11,from_=0,to=59,wrap=True,textvariable=self.eminstr,width=2,state="readonly")
        self.esecstr=tk.StringVar(self,'00')
        self.esecstr.trace("w",self.etrace_var_s)
        self.elast_value_s = ""
        self.esec = tk.Spinbox(Frame11,from_=0,to=59,wrap=True,textvariable=self.esecstr,width=2,state="readonly")
        self.ehour.grid(row=5,column=1)
        self.emin.grid(row=5,column=2)
        self.esec.grid(row=5,column=3)
        
        L1 = tk.Label(Frame10, text="      Date :" , font = 20)
        L1.grid(row=1, column = 0)
        L2 = tk.Label(Frame11, text="Start Time :" , font = 20)
        L2.grid(row=4, column = 0)
        L3 = tk.Label(Frame11, text="  End Time :" , font = 20)
        L3.grid(row=5, column = 0)
        self.L4 = tk.Label(Frame10, text="" , font = 20)
        self.L4.place(x=230, y=30)

    def strace_var_m(self,*args):
        if self.slast_value_m == "59" and self.sminstr.get() == "0":
            self.shourstr.set(int(self.shourstr.get())+1 if self.shourstr.get() !="23" else 0)
        self.slast_value_m = self.sminstr.get()

    def strace_var_s(self,*args):
        if self.slast_value_s == "59" and self.ssecstr.get() == "0":
            self.sminstr.set(int(self.sminstr.get())+1 if self.sminstr.get() !="59" else 0)
        self.slast_value_s = self.ssecstr.get()

    def etrace_var_m(self,*args):
        if self.elast_value_m == "59" and self.eminstr.get() == "0":
            self.ehourstr.set(int(self.ehourstr.get())+1 if self.ehourstr.get() !="23" else 0)
        self.elast_value_m = self.eminstr.get()

    def etrace_var_s(self,*args):
        if self.elast_value_s == "59" and self.esecstr.get() == "0":
            self.eminstr.set(int(self.eminstr.get())+1 if self.eminstr.get() !="59" else 0)
        self.elast_value_s = self.esecstr.get()

    def exit(self):
        self.start = 0
        self.master.destroy()
        
    def click(self,event):
        # RIGHT click (NEXT)
        if event.button == 3:
            self.s_plot += self.plot_length
            self.legend = 1
            if self.s_plot > len(self.log) -1 - self.plot_length :
                self.s_plot = len(self.log) - 1 - self.plot_length
                self.legend = 2
            self.read_plot()
        # LEFT click (PREVIOUS)
        elif event.button == 1 :
            self.s_plot -= self.plot_length
            self.legend = 1
            if self.s_plot < 0:
                self.s_plot = 0
                self.legend = 0
            self.read_plot()

    def Plot(self):
        self.L4.config(text= "      ")
        dat = datetime.datetime.strptime(self.in_date.get(), '%y-%m-%d').strftime('%y-%m-%d')
        stim = self.shour.get() + ":" +  self.smin.get() + ":" +  self.ssec.get()
        self.start_time = datetime.datetime.strptime(stim, '%H:%M:%S').strftime('%H:%M:%S')
        etim = self.ehour.get() + ":" +  self.emin.get() + ":" +  self.esec.get()
        self.end_time = datetime.datetime.strptime(etim, '%H:%M:%S').strftime('%H:%M:%S')
        
        self.start = 0
        self.s_plot = 0
        if self.count == 2:
            self.count = 1
        elif self.count == 1:
            self.count = 2
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
                plt.xlabel('Log: ' + self.log_file + " - Clicks: LEFT for PREVIOUS, RIGHT for NEXT")
            elif self.legend == 0:
                plt.xlabel('Log: ' + self.log_file + " - Clicks: RIGHT for NEXT")
            elif self.legend == 2:
                plt.xlabel('Log: ' + self.log_file + " - Clicks: LEFT for PREVIOUS") 
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

            # start animation
            if self.count == 0:
                plot_thread = threading.Thread(target=self.thread_plot)
                plot_thread.start()
                self.count = 1
            if self.count == 1:        
                # delete temporary filtered log
                if os.path.exists('/run/shm/plot.log'): 
                    os.remove('/run/shm/plot.log')
             
                # generate temporary filtered log
                objFile = open(self.log_file, "r")
                count_x = 0
                s_count = 0
                e_count = 0
                for line in objFile:
                    if self.start_time in line:
                        s_count = count_x
                    if self.end_time in line:
                        e_count = count_x
                    count_x += 1       
                objFile.close()
                # if no required time entries are found
                if s_count == 0:
                    s_count = ((int(self.start_time[0:2]) * 3600 + int(self.start_time[3:5]) * 60 + int(self.start_time[6:8]) + 1))
                if e_count == 0:
                    e_count = ((int(self.end_time[0:2]) * 3600 + int(self.end_time[3:5]) * 60 + int(self.end_time[6:8])))
                if e_count <= s_count or e_count - s_count < self.plot_length:
                    e_count = s_count + self.plot_length 
                start_count = str(s_count + 1)
                end_count = str(e_count + 1)
                path = "sed -n " +  start_count  + "," +  end_count + "p " + '"' + self.log_file + '"' + " >> /run/shm/plot.log"
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
                    if line[0:1] == "d":
                        counter1 = line.count(' ')
                        counter2 = line.count('.')
                        if counter1 == 6 and counter2 == 5:
                            self.log.append(line)
                    self.stop = 1
                    while line and self.stop:
                        line = file.readline()
                        self.log.append(line)
                self.count = 2
            # put values in lists for plotting
            if len(self.log) >= self.plot_length:
                for x in range(self.s_plot,self.s_plot + self.plot_length):
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
