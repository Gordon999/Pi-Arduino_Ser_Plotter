                elif end_count > self.count_x:
                    end_count = self.count_x
                    start_count = end_count - self.plot_length
                    
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
                            # find mid_time to display
                            if x == int(self.plot_length/2) + 1:
                                self.mid_time3 = t
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
