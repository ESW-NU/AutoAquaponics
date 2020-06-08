#Stop code with Ctrl+C in shell, the stop button deletes
#the graph and csv file for some reason

#import necessary modules and initialize I2C bus
import time
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
#import board module (ADS1115)
import adafruit_ads1x15.ads1115 as ADS
#import ADS1x15 library's version of AnalogIn
from adafruit_ads1x15.analog_in import AnalogIn
#create ADS object
ads = ADS.ADS1115(i2c)
ads.gain = 2/3
#single ended mode read for pin 0 and 1
chan = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1) 
    
#importing/initializing for plotting/saving
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from time import sleep
import csv

plt.ion()
max_voltage = 5
min_voltage = 0
voltage_list = []
voltage1_list = []
t = []
ii = 0
print("{:>5}\t{:>5}".format('P0','P1'))

#create subplots and set axis
fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle('Aquaponic Sensors')
ax1.set_ylabel('pH (V)')
ax1.set_ylim([2,4])
ax2.set_ylabel('Temperature Voltage (V)')
ax2.set_ylim([0,5])
ax2.set_xlabel('Time (s)')

#import date and time for timestamp
from datetime import datetime

#clear csv file on flash drive
f = open("/media/pi/68D2-7E93/test2.csv", "w")
f.truncate()
f.close()

#save data into test.csv on flash drive by appending new row
with open('/media/pi/68D2-7E93/test2.csv','a+',newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Date and Time","P0 (V)", "P1 (V)"])
    f.close()
    while True:
        #define output of both channels
        voltage = round(chan.voltage, 3)
        voltage1 = round(chan1.voltage, 3)
        print("{:>5}\t{:>5}".format(voltage, voltage1)) #could remove
        #append new output to existing lists
        voltage_list.append(voltage)
        voltage1_list.append(voltage1)
        t.append(ii)
        ii = ii+1 #time counter
        sleep(1)
        #append data to csv file & plot every 5 seconds
        if ii/5 == int(ii/5):
            now = datetime.now()
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            writer.writerow([dt_string, voltage, voltage1])
            f.close()
            #plot the lists
            ax1.plot(t, voltage_list, 'tab:blue')
            ax2.plot(t, voltage1_list, 'tab:red')
#make legend (only for plotting mult lines on single graph)
        #label1 = mpatches.Patch(color='red', label='Voltage 1')
        #label2 = mpatches.Patch(color='blue', label='Voltage 2')
        #plt.legend(handles=[label1, label2], bbox_to_anchor=(0., 1.01, 1., .102), loc='lower left',
           #ncol=2, mode="expand", borderaxespad=0.)
#actually draws plot
            plt.draw()
            plt.pause(0.001) #some weird thing that makes the plot update, doesn't work without this pause
        