def fakeDataLogger(file_name):
    import random
    from time import sleep
    import csv
    import os
    from datetime import datetime
    raw_voltage_list = []
    raw_voltage1_list = []
    voltage_list = []
    voltage1_list = []
    ii = 0
    loc = os.path.expanduser("~/Desktop/") + file_name
    with open(loc,'a+',newline='') as file:
            writer = csv.writer(file)
            #define output of both channels, round to 3 decimals
            while True:
                raw_voltage = random.choice([2.322,2.444,2.533,2.666])
                raw_voltage1 = random.choice([2.322,2.444,2.533,2.666])
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
