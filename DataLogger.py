#importing/initializing for plotting/saving
def DataLogger(file_name):
    #importing data from other function
    from getData import getData
    #importing/initializing for plotting/saving    
    #import matplotlib.pyplot as plt
#    import matplotlib.patches as mpatches
    from time import sleep
    import csv
    #plt.ion()
    voltage_list = []
    voltage1_list = []
    t = []
    ii = 0
    #print("{:>5}\t{:>5}".format('P0','P1'))

    #create subplots and set axis (not needed after GUI works)
#    fig, (ax1, ax2) = plt.subplots(nrows=2, num=1)
#    fig.suptitle('Aquaponic Sensors')
#    ax1.set_ylabel('pH (V)')
#    ax1.set_ylim([2,4])
#    ax2.set_ylabel('Temperature Voltage (V)')
#    ax2.set_ylim([0,5])
#    ax2.set_xlabel('Time (s)')

    #import date and time for timestamp
    from datetime import datetime

    #clear csv file on flash drive
    loc = "/media/pi/68D2-7E93/" + file_name
    f = open(loc, "w")
    f.truncate()
    f.close()

    #save data into test.csv on flash drive by appending new row
    with open(loc,'a+',newline='') as file:
        writer = csv.writer(file)
        #writer.writerow(["Date and Time","P0 (V)", "P1 (V)"])
        file.flush()
        #define output of both channels
        while True:
            voltage = round(getData()[0], 3)
            voltage1 = round(getData()[1], 3)
            #print("{:>5}\t{:>5}".format(voltage, voltage1))
        #append new output to existing lists
            voltage_list.append(voltage)
            voltage1_list.append(voltage1)
            t.append(ii)
            ii = ii+1 #time counter
            sleep(1)
            #append data to csv file & plot
            if ii/5 == int(ii/5):
                now = datetime.now()
                dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                writer.writerow([dt_string, next(reversed(t)), voltage, voltage1])
                file.flush()
                #plot the lists
                #ax1.plot(t, voltage_list, 'tab:blue')
                #ax2.plot(t, voltage1_list, 'tab:red')
#make legend (only for plotting mult lines on single graph)
        #label1 = mpatches.Patch(color='red', label='Voltage 1')
        #label2 = mpatches.Patch(color='blue', label='Voltage 2')
        #plt.legend(handles=[label1, label2], bbox_to_anchor=(0., 1.01, 1., .102), loc='lower left',
           #ncol=2, mode="expand", borderaxespad=0.)
#actually draws plot
                #plt.draw()
                #plt.pause(0.0001) #some weird thing that makes the plot update, doesn't work without this pause