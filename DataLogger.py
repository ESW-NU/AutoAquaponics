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
    raw_voltage_list = []
    raw_voltage1_list = []
    voltage_list = []
    voltage1_list = []
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

    #clear csv file on flash drive, comment out if not needed
    loc = "/media/pi/68D2-7E93/" + file_name
    #f = open(loc, "w")
    #f.truncate()
    #f.close()

    #save data into test.csv on flash drive by appending new row
    with open(loc,'a+',newline='') as file:
        writer = csv.writer(file)
        #comment out these headings 
        #writer.writerow(["Date and Time","P0 (V)", "P1 (V)"])
        #file.flush()
        #define output of both channels, round to 3 decimals
        while True:
            raw_voltage = getData()[0]
            raw_voltage1 = getData()[1]
            #print("{:>5}\t{:>5}".format(voltage, voltage1))
        #append new output to existing lists
            raw_voltage_list.append(raw_voltage)
            raw_voltage1_list.append(raw_voltage1)
            ii = ii+1
            sleep(1)
            #add the denoised data to voltage list evey 5s
            if ii % 5 == 0:
                voltage = round(sum(raw_voltage_list)/len(raw_voltage_list),3)
                voltage1 = round(sum(raw_voltage1_list)/len(raw_voltage1_list),3)
                voltage_list.append(voltage)
                voltage1_list.append(voltage1)
            #keep lists short to prevent using too much memory
                raw_voltage_list = raw_voltage_list[-5:]
                raw_voltage1_list = raw_voltage1_list[-5:]
                voltage_list = voltage_list[-20:]
                voltage1_list = voltage_list[-20:]
                #append data to csv file & plot
                now = datetime.now()
                dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                writer.writerow([dt_string, voltage, voltage1])
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
