# Pi-Arduino_Ser_Plotter
The Arduino IDE provides a very convenient serial plotter. The drawback is that you need to load the complete IDE to use it.
The other drawback is also that this functionality is not easily tweakable by the user.
The standard plot has also only numbers on the x-axe, having the time is currently not foreseen.

This project intends to provide a similar plotter functionality that can be invoked directly from Python, with the advantage that everybody can tweak it to his own needs.
Currently the program is written for plotting five floating point values at a 1 second pace, that are issued on the serial port separated by spaces e.g. here an example for plotting a value and 4 derivates (long-term average, smoothed value, maximum and minimum):

Serial.print(Avg);  Serial.print(" "); Serial.println(A0dB); Serial.print(" "); Serial.print(A0dBslow); Serial.print(" "); Serial.print(A0Min);   Serial.print(" "); Serial.println(A0Max); 

The first line of the serial flow may contain the descriptors with same number of  parameters.
The data will be plotted for the last 5 min. with an picture update every 10 seconds to reduce the workload.
Additionally the data is written to a log file for further usage.

Changelog:

-Avoiding the errors at the beginning, when python gets an empty line and the line with headers (done)

-Classifiying the line type into waiting for sync, header, data and error (done)

-Changing the log to display each line with the line type at the end (done)

-Making the number of plots depending on the header line (tbd)

-Making the serial port an optional, persistent parameter of the python script (tbd)

-Changing the log to be two alternating hourly logs (odd,even) (tbd)

-Elaborating stats on the past hour, day, month... (tbd)

-Writing at the end of every hour the last log into a disk file and appending the hourly stats...(tbd)

