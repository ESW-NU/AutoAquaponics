import datetime
from typing import Container
#import led info, replace with relay info
#from gpiozero import PWMLED
#LED1 = PWMLED(17)
#import DataLogger.py
from DataLogger import DataLogger
#import tkinter for GUI
import tkinter as tk
from tkinter import *
from tkinter import ttk
#font types
TITLE_FONT = ("Verdana", 14,) #"bold")
LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)
#import stuff for graph
import matplotlib
import matplotlib.ticker as mticker
from matplotlib import pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import csv
#import/enable garbage collector to clear memory
import gc
gc.enable()
#import animation to make graph live
import matplotlib.animation as animation
from matplotlib import style
style.use("seaborn-darkgrid")
#import vertical scroll bar
from vertical_scroll_frame import VerticalScrolledFrame
#set file path
file_path = "/Users/Bill Yen/Desktop/NU Urban Ag/test3.csv"
#set path for file that stores Settings/Control Panel config
config_path = "/Users/Bill Yen/Desktop/NU Urban Ag/config.csv"
#create config file if it doesn't already exist
create_file = open(config_path, "a+")
create_file.close()
#initialize channel_buttons_config
with open(config_path, "r") as file:
    config_settings = list(csv.reader(file))
    if len(config_settings) != 3:
        channel_buttons_config = [-1]*16
    else:
        channel_buttons_config = config_settings[0]
    file.close()
#create figure for plots and set figure size/layout
f = Figure(figsize=(8.6,17.5), dpi=100)
f.subplots_adjust(top=0.993, bottom=0.015)
#plots
plot1 = f.add_subplot(6,2,1)
plot2 = f.add_subplot(6,2,2)
plot3 = f.add_subplot(6,2,3)
plot4 = f.add_subplot(6,2,4)
plot5 = f.add_subplot(6,2,5)
plot6 = f.add_subplot(6,2,6)
plot7 = f.add_subplot(6,2,7)
plot8 = f.add_subplot(6,2,8)
plot9 = f.add_subplot(6,2,9)
plot10 = f.add_subplot(6,2,10)
plot11 = f.add_subplot(6,2,11)
#animate function
def animate(ii):
    pullData = open(file_path,"r").read()
    dataList = pullData.split('\n')
    open(file_path,"r").close()
    #setting timeframe and making sure GUI runs on short CSVs too
    input_file = open(file_path, "r")
    reader_file = csv.reader(input_file)
    dataLen = len(list(reader_file))
    if dataLen < 240:
        timeframe = -dataLen
    else:
        timeframe = int(-240)
    input_file.close()
    #make all the x and y variable lists
    dataList = dataList[timeframe:]
    tList = []
    vList = []
    v1List = []
    for eachLine in dataList:
        if len(eachLine) >1:
            timedate, voltage, voltage1 = eachLine.split(',')
            tList.append(datetime.datetime.strptime(timedate, "%m/%d/%Y %I:%M:%S %p"))
            vList.append(float(voltage))
            v1List.append(float(voltage1))
            #keep the lists to a reasonable length to save memory
            tList = tList[timeframe:]
            vList = vList[timeframe:]
            v1List = v1List[timeframe:]
    #plot graphs
    plot1.clear()
    plot2.clear()
    #plot1.plot(tList, vList, 'r')
    #plot2.plot(tList, v1List, 'b')
    #this is to get the reference to fill the graph, can change to more meaningful
    #values later so we can change graph fill color based on water parameter
    listofzeros = [0] * len(tList)
    #add labels and config axis
    plot1.set_ylabel("pH (v)")
    plot1.set_ylim(2,4)
    plot2.set_ylabel("Temperature (v)")
    plot2.set_ylim(0,5)
    #show half the length of our timeframe, set functionality to let user scroll
    #to next half later
    plot1.set_xlim(tList[int(timeframe/2)], tList[-1])
    plot2.set_xlim(tList[int(timeframe/2)], tList[-1])
    #slant the x axis tick labels for extra coolness
    for label in plot1.xaxis.get_ticklabels():
        label.set_rotation(10)
    for label in plot2.xaxis.get_ticklabels():
        label.set_rotation(10)
    #make sure the xticks aren't overlapping
    plot1.xaxis.set_major_locator(mticker.MaxNLocator(nbins=4))
    plot2.xaxis.set_major_locator(mticker.MaxNLocator(nbins=4))
    #fill the graphs
    plot1.fill_between(tList, vList,
                       where=(vList > listofzeros),
                       facecolor = 'r', edgecolor = 'r', alpha = 0.5)
    plot2.fill_between(tList, v1List,
                       where=(v1List > listofzeros),
                       facecolor = 'b', edgecolor = 'b', alpha = 0.5)
    #collect garbage
    gc.collect()
#initialization
class AllWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #add title
        tk.Tk.wm_title(self, "NU Aquaponics")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        #create navigation menu
        menubar = tk.Menu(container)
        navimenu = tk.Menu(menubar, tearoff=0)
        #add new items in navimenu to navigate to pages
        navimenu.add_command(label="Dashboard", command=lambda: self.show_frame(HomePage))
        navimenu.add_command(label="Control Panel", command=lambda: self.show_frame(ControlPanel))
        navimenu.add_command(label="Video Stream", command=lambda: self.show_frame(VideoStream))
        navimenu.add_command(label="Settings", command=lambda: self.show_frame(Settings))
        #add separator line
        navimenu.add_separator()
        #add quit button in menu that triggers a command
        navimenu.add_command(label="Quit", command=self.die)
        #actually add the bar
        menubar.add_cascade(label="Menu", menu=navimenu)
        tk.Tk.config(self, menu=menubar)
        #show the frames
        self.frames = {}
        #remember to add page to this list when making new ones
        for F in (HomePage, ControlPanel, Settings, VideoStream):
            frame = F(container, self)
            #set background color for the pages
            frame.config(bg='white')
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(HomePage)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
    #end program fcn triggered by quit button
    def die(self):
        exit()
#add home page
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        #bring up vertical scroll frame and place it
        scframe = VerticalScrolledFrame(self)
        scframe.place(x=130, y=40)
        #bring up canvas with plot in the frame with vertical scroll bar
        canvas = FigureCanvasTkAgg(f, scframe.interior)
        canvas.draw()
        #create title label
        label = tk.Label(self, text="Dashboard", bg='white', font = TITLE_FONT)
        label.place(x=460, y=10)
        #embed graph into canvas
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        #add navigation bar
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        #color variables
        pHcolor = "white"
        #data table labels
        table_title = tk.Label(self, text="Data Summary", bg="white", font = LARGE_FONT)
        table_title.place(x=28, y=40)
        leak_label = tk.Label(self, text="Leakage", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        leak_label.place(x=5, y=65)
        waterlvl_label = tk.Label(self, text="Water Level", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        waterlvl_label.place(x=5, y=87)
        pH_label = tk.Label(self, text="pH", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        pH_label.place(x=5, y=109)
        wtemp_label = tk.Label(self, text="Water Temp", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        wtemp_label.place(x=5, y=131)
        atemp_label = tk.Label(self, text="Air Temp", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        atemp_label.place(x=5, y=153)
        NO3_label = tk.Label(self, text="Nitrate", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        NO3_label.place(x=5, y=175)
        TDS_label = tk.Label(self, text="TDS", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        TDS_label.place(x=5, y=197)
        DO_label = tk.Label(self, text="DO", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        DO_label.place(x=5, y=219)
        NH3_label = tk.Label(self, text="Ammonia", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        NH3_label.place(x=5, y=241)
        PO4_label = tk.Label(self, text="Phosphate", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        PO4_label.place(x=5, y=263)
        humidity_label = tk.Label(self, text="Humidity", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        humidity_label.place(x=5, y=285)
        flowrate_label = tk.Label(self, text="Flow Rate", fg="black", bg=pHcolor,
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1, anchor=W, justify=LEFT)
        flowrate_label.place(x=5, y=307)
        #updating live texts
        leak_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        leak_data.place(x=91, y=65)
        waterlvl_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        waterlvl_data.place(x=91, y=87)
        pH_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        pH_data.place(x=91, y=109)
        wtemp_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        wtemp_data.place(x=91, y=131)
        atemp_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        atemp_data.place(x=91, y=153)
        NO3_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        NO3_data.place(x=91, y=175)
        TDS_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        TDS_data.place(x=91, y=197)
        DO_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        DO_data.place(x=91, y=219)
        NH3_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        NH3_data.place(x=91, y=241)
        PO4_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        PO4_data.place(x=91, y=263)
        humidity_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        humidity_data.place(x=91, y=285)
        flowrate_data = tk.Label(self, text="Loading", fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=10, height=1)
        flowrate_data.place(x=91, y=307)
#function to update live text
        def GetValues():
            pullData = open(file_path,"r").read()
            dataList = pullData.split('\n')
            for eachLine in dataList:
                if len(eachLine) >1:
                    #add to this list of data read as we add more sensors
                    timedate, voltage, voltage1 = eachLine.split(',')
                    pH_data.config(text = voltage)
                    wtemp_data.config(text = voltage1)
            open(file_path,"r").close()
            gc.collect()
            self.after(5000, GetValues)
        self.after(5000, GetValues)

#add control panel page
class ControlPanel(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
    #text labels
        Title = tk.Label(self, text="Control Panel", bg= 'white', font = TITLE_FONT)
        Title.grid(row =0, columnspan = 14)

    #navigation button
        navibutton1 = ttk.Button(self, text="Back to Dashboard",
                            command=lambda: controller.show_frame(HomePage))
        navibutton1.grid(row = 1, columnspan = 14)

    #Save button
        self.saveButton= ttk.Button(self, text="Save", command=self.popup)
        self.saveButton.grid(row=2, columnspan=14, pady=(0,0))
    #Discard button
        self.discardButton= ttk.Button(self, text="Discard", command=self.discard)
        self.discardButton.grid(row=3, columnspan=14, pady=(0,20))

    #channel labels
        Channel_1 = tk.Label(self, text="1", bg='white', font = SMALL_FONT)
        Channel_1.grid(row = 4, column=1)
        Channel_2 = tk.Label(self, text="2", bg='white', font = SMALL_FONT)
        Channel_2.grid(row = 5, column=1)
        Channel_3 = tk.Label(self, text="3", bg='white', font = SMALL_FONT)
        Channel_3.grid(row = 6, column=1)
        Channel_4 = tk.Label(self, text="4", bg='white', font = SMALL_FONT)
        Channel_4.grid(row = 7, column=1)
        Channel_5 = tk.Label(self, text="5", bg='white', font = SMALL_FONT)
        Channel_5.grid(row = 8, column=1)
        Channel_6 = tk.Label(self, text="6", bg='white', font = SMALL_FONT)
        Channel_6.grid(row = 9, column=1)
        Channel_7 = tk.Label(self, text="7", bg='white', font = SMALL_FONT)
        Channel_7.grid(row = 10, column=1)
        Channel_8 = tk.Label(self, text="8", bg='white', font = SMALL_FONT)
        Channel_8.grid(row = 11, column=1, pady=(0,20))
        Channel_9 = tk.Label(self, text="9", bg='white', font = SMALL_FONT)
        Channel_9.grid(row = 4, column=7, padx=(40,0))
        Channel_10 = tk.Label(self, text="10", bg='white', font = SMALL_FONT)
        Channel_10.grid(row = 5, column=7, padx=(40,0))
        Channel_11 = tk.Label(self, text="11", bg='white', font = SMALL_FONT)
        Channel_11.grid(row = 6, column=7, padx=(40,0))
        Channel_12 = tk.Label(self, text="12", bg='white', font = SMALL_FONT)
        Channel_12.grid(row = 7, column=7, padx=(40,0))
        Channel_13 = tk.Label(self, text="13", bg='white', font = SMALL_FONT)
        Channel_13.grid(row = 8, column=7, padx=(40,0))
        Channel_14 = tk.Label(self, text="14", bg='white', font = SMALL_FONT)
        Channel_14.grid(row = 9, column=7, padx=(40,0))
        Channel_15 = tk.Label(self, text="15", bg='white', font = SMALL_FONT)
        Channel_15.grid(row = 10, column=7, padx=(40,0))
        Channel_16 = tk.Label(self, text="16", bg='white', font = SMALL_FONT)
        Channel_16.grid(row = 11, column=7, padx=(40,0), pady=(0,20))
    #relay control buttons
        #relays 1-8
        self.channelButton1 = tk.Button(self, text="Channel OFF",
                                        bg= "red", fg= "white",
                                        width=10, height=1,
                                        command=self.channel_1)
        self.channelButton1.grid(row = 4, column=2)
        self.channelButton2 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_2)
        self.channelButton2.grid(row = 5, column=2)
        self.channelButton3 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_3)
        self.channelButton3.grid(row = 6, column=2)
        self.channelButton4 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_4)
        self.channelButton4.grid(row = 7, column=2)
        self.channelButton5 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_5)
        self.channelButton5.grid(row = 8, column=2)
        self.channelButton6 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_6)
        self.channelButton6.grid(row = 9, column=2)
        self.channelButton7 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_7)
        self.channelButton7.grid(row = 10, column=2)
        self.channelButton8 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_8)
        self.channelButton8.grid(row = 11, column=2, pady=(0,20))
        #relays 9-16
        self.channelButton9 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_9)
        self.channelButton9.grid(row = 4, column=8)
        self.channelButton10 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_10)
        self.channelButton10.grid(row = 5, column=8)
        self.channelButton11 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_11)
        self.channelButton11.grid(row = 6, column=8)
        self.channelButton12 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_12)
        self.channelButton12.grid(row = 7, column=8)
        self.channelButton13 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_13)
        self.channelButton13.grid(row = 8, column=8)
        self.channelButton14 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_14)
        self.channelButton14.grid(row = 9, column=8)
        self.channelButton15 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_15)
        self.channelButton15.grid(row = 10, column=8)
        self.channelButton16 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         width=10, height=1,
                                         command=self.channel_16)
        self.channelButton16.grid(row = 11, column=8, pady=(0,20))

    #Entry widgets for Channel OverWrite Times
        #Labels for each:
        tk.Label(self, text="Turn on for:", bg="white").grid(row=4, column=3)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=5, column=3)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=6, column=3)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=7, column=3)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=8, column=3)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=9, column=3)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=10, column=3)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=11, column=3, pady=(0,10))
        tk.Label(self, text="Turn on for:", bg="white").grid(row=4, column=9)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=5, column=9)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=6, column=9)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=7, column=9)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=8, column=9)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=9, column=9)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=10, column=9)
        tk.Label(self, text="Turn on for:", bg="white").grid(row=11, column=9, pady=(0,10))

        tk.Label(self, text="Turn off for:", bg="white").grid(row=4, column=5)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=5, column=5)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=6, column=5)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=7, column=5)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=8, column=5)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=9, column=5)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=10, column=5)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=11, column=5, pady=(0,10))
        tk.Label(self, text="Turn off for:", bg="white").grid(row=4, column=11)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=5, column=11)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=6, column=11)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=7, column=11)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=8, column=11)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=9, column=11)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=10, column=11)
        tk.Label(self, text="Turn off for:", bg="white").grid(row=11, column=11, pady=(0,10))

        #Entries
        self.on1 = tk.Entry(self, width = 10)
        self.on1.grid(row = 4, column = 4)
        self.on2=tk.Entry(self, width = 10)
        self.on2.grid(row = 5, column = 4)
        self.on3=tk.Entry(self, width = 10)
        self.on3.grid(row = 6, column = 4)
        self.on4=tk.Entry(self, width = 10)
        self.on4.grid(row = 7, column = 4)
        self.on5=tk.Entry(self, width = 10)
        self.on5.grid(row = 8, column = 4)
        self.on6=tk.Entry(self, width = 10)
        self.on6.grid(row = 9, column = 4)
        self.on7=tk.Entry(self, width = 10)
        self.on7.grid(row = 10, column = 4)
        self.on8=tk.Entry(self, width = 10)
        self.on8.grid(row = 11, column =4, pady=(0,10))
        self.on9=tk.Entry(self, width = 10)
        self.on9.grid(row=4, column=10)
        self.on10=tk.Entry(self, width = 10)
        self.on10.grid(row=5, column=10)
        self.on11=tk.Entry(self, width = 10)
        self.on11.grid(row=6, column=10)
        self.on12=tk.Entry(self, width = 10)
        self.on12.grid(row=7, column=10)
        self.on13=tk.Entry(self, width = 10)
        self.on13.grid(row=8, column=10)
        self.on14=tk.Entry(self, width = 10)
        self.on14.grid(row=9, column=10)
        self.on15=tk.Entry(self, width = 10)
        self.on15.grid(row=10, column=10)
        self.on16=tk.Entry(self, width = 10)
        self.on16.grid(row=11, column=10, pady=(0,10))
        self.off1=tk.Entry(self, width = 10)
        self.off1.grid(row=4, column = 6)
        self.off2=tk.Entry(self, width = 10)
        self.off2.grid(row=5, column = 6)
        self.off3=tk.Entry(self, width = 10)
        self.off3.grid(row=6, column = 6)
        self.off4=tk.Entry(self, width = 10)
        self.off4.grid(row=7, column = 6)
        self.off5=tk.Entry(self, width = 10)
        self.off5.grid(row=8, column = 6)
        self.off6=tk.Entry(self, width = 10)
        self.off6.grid(row=9, column = 6)
        self.off7=tk.Entry(self, width = 10)
        self.off7.grid(row=10, column = 6)
        self.off8=tk.Entry(self, width = 10)
        self.off8.grid(row=11, column =6, pady=(0,10))
        self.off9=tk.Entry(self, width = 10)
        self.off9.grid(row=4, column = 12)
        self.off10=tk.Entry(self, width = 10)
        self.off10.grid(row=5, column=12)
        self.off11=tk.Entry(self, width = 10)
        self.off11.grid(row=6, column=12)
        self.off12=tk.Entry(self, width = 10)
        self.off12.grid(row=7, column=12)
        self.off13=tk.Entry(self, width = 10)
        self.off13.grid(row=8, column=12)
        self.off14=tk.Entry(self, width = 10)
        self.off14.grid(row=9, column=12)
        self.off15=tk.Entry(self, width = 10)
        self.off15.grid(row=10, column=12)
        self.off16=tk.Entry(self, width = 10)
        self.off16.grid(row=11, column= 12, pady=(0,10))
        #calls on discard() to initialize entry values
        self.discard()
        #call on the channel fcns to initialize button toggles
        self.init_channels()
        #Tells user what to input
        tk.Label(self, text="*Input Time in Hours", bg="white").grid(row=12, columnspan=14)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(13, weight=1)

        #fcn triggered by save button
    def popup(self):
        #get the input of all entries as a float value to the hundredth place
        self.popup = tk.Tk()
        self.popup.wm_title("Message")
        label = ttk.Label(self.popup, text="Are you sure you want to save?", font=MEDIUM_FONT)
        label.grid(row=0, columnspan=14, pady=(10,20), padx = (5,5))
        YesB = ttk.Button(self.popup, text="YES", command = self.save)
        YesB.grid(row=1, column=1, padx =(23,10), pady = (0,10))
        NoB = ttk.Button(self.popup, text="NO", command = self.popup.destroy)
        NoB.grid(row=1, column=2, pady = (0,10))
        self.popup.mainloop()
    #triggered if user press YES in popup window
    def save(self):
        on_config = [round(float(self.on1.get()),2), round(float(self.on2.get()),2), round(float(self.on3.get()),2), round(float(self.on4.get()),2),
        round(float(self.on5.get()),2), round(float(self.on6.get()),2), round(float(self.on7.get()),2), round(float(self.on8.get()),2),
        round(float(self.on9.get()),2), round(float(self.on10.get()),2), round(float(self.on11.get()),2), round(float(self.on12.get()),2),
        round(float(self.on13.get()),2), round(float(self.on14.get()),2), round(float(self.on15.get()),2), round(float(self.on16.get()),2)]
        off_config = [round(float(self.off1.get()),2), round(float(self.off2.get()),2), round(float(self.off3.get()),2), round(float(self.off4.get()),2),
        round(float(self.off5.get()),2), round(float(self.off6.get()),2), round(float(self.off7.get()),2), round(float(self.off8.get()),2),
        round(float(self.off9.get()),2), round(float(self.off10.get()),2), round(float(self.off11.get()),2), round(float(self.off12.get()),2),
        round(float(self.off13.get()),2), round(float(self.off14.get()),2), round(float(self.off15.get()),2), round(float(self.off16.get()),2)]
        #write two rows of data into csv, erase past info
        with open(config_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([channel_buttons_config,on_config,off_config])
            file.flush()
        #destroy popup window after writing file
        self.popup.destroy()
        #fcn triggered by discard button
    def discard(self):
        #Delete current values
        self.on1.delete(0, END)
        self.on2.delete(0, END)
        self.on3.delete(0, END)
        self.on4.delete(0, END)
        self.on5.delete(0, END)
        self.on6.delete(0, END)
        self.on7.delete(0, END)
        self.on8.delete(0, END)
        self.on9.delete(0, END)
        self.on10.delete(0, END)
        self.on11.delete(0, END)
        self.on12.delete(0, END)
        self.on13.delete(0, END)
        self.on14.delete(0, END)
        self.on15.delete(0, END)
        self.on16.delete(0, END)
        self.off1.delete(0, END)
        self.off2.delete(0, END)
        self.off3.delete(0, END)
        self.off4.delete(0, END)
        self.off5.delete(0, END)
        self.off6.delete(0, END)
        self.off7.delete(0, END)
        self.off8.delete(0, END)
        self.off9.delete(0, END)
        self.off10.delete(0, END)
        self.off11.delete(0, END)
        self.off12.delete(0, END)
        self.off13.delete(0, END)
        self.off14.delete(0, END)
        self.off15.delete(0, END)
        self.off16.delete(0, END)
        #Get last saved values
        with open(config_path, "r") as file:
            config_settings = list(csv.reader(file))
            if len(config_settings) != 3:
                #initialize the file by creating and writing to csv
                with open(config_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows([channel_buttons_config,[0]*16,[0]*16])
                    config_settings = [channel_buttons_config,[0]*16,[0]*16]
                    file.flush()
                    file.close()
            self.on1.insert(0, config_settings[1][0])
            self.on2.insert(0, config_settings[1][1])
            self.on3.insert(0, config_settings[1][2])
            self.on4.insert(0, config_settings[1][3])
            self.on5.insert(0, config_settings[1][4])
            self.on6.insert(0, config_settings[1][5])
            self.on7.insert(0, config_settings[1][6])
            self.on8.insert(0, config_settings[1][7])
            self.on9.insert(0, config_settings[1][8])
            self.on10.insert(0, config_settings[1][9])
            self.on11.insert(0, config_settings[1][10])
            self.on12.insert(0, config_settings[1][11])
            self.on13.insert(0, config_settings[1][12])
            self.on14.insert(0, config_settings[1][13])
            self.on15.insert(0, config_settings[1][14])
            self.on16.insert(0, config_settings[1][15])
            self.off1.insert(0, config_settings[2][0])
            self.off2.insert(0, config_settings[2][1])
            self.off3.insert(0, config_settings[2][2])
            self.off4.insert(0, config_settings[2][3])
            self.off5.insert(0, config_settings[2][4])
            self.off6.insert(0, config_settings[2][5])
            self.off7.insert(0, config_settings[2][6])
            self.off8.insert(0, config_settings[2][7])
            self.off9.insert(0, config_settings[2][8])
            self.off10.insert(0, config_settings[2][9])
            self.off11.insert(0, config_settings[2][10])
            self.off12.insert(0, config_settings[2][11])
            self.off13.insert(0, config_settings[2][12])
            self.off14.insert(0, config_settings[2][13])
            self.off15.insert(0, config_settings[2][14])
            self.off16.insert(0, config_settings[2][15])
            file.close()
            gc.collect()
    #save channel button settings
    def channel_buttons_save(self):
        with open(config_path, "r") as file:
            config_settings = list(csv.reader(file))
            config_settings[0] = channel_buttons_config
            file.close()
            with open(config_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(config_settings)
                file.flush()
                file.close()
                gc.collect()
        #fcn that initializes control buttons
    def init_channels(self):
        if int(channel_buttons_config[0]) == -1:
            self.channelButton1.configure(bg= "red")
            self.channelButton1.configure(text = "Channel OFF")
        elif int(channel_buttons_config[0]) == 1:
            self.channelButton1.configure(bg= "green")
            self.channelButton1.configure(text = "Channel ON")
        elif int(channel_buttons_config[0]) == 0:
            self.channelButton1.configure(bg= "purple")
            self.channelButton1.configure(text = "Timer ON")
        if int(channel_buttons_config[1]) == -1:
            self.channelButton2.configure(bg= "red")
            self.channelButton2.configure(text = "Channel OFF")
        elif int(channel_buttons_config[1]) == 1:
            self.channelButton2.configure(bg= "green")
            self.channelButton2.configure(text = "Channel ON")
        elif int(channel_buttons_config[1]) == 0:
            self.channelButton2.configure(bg= "purple")
            self.channelButton2.configure(text = "Timer ON")
        if int(channel_buttons_config[2]) == -1:
            self.channelButton3.configure(bg= "red")
            self.channelButton3.configure(text = "Channel OFF")
        elif int(channel_buttons_config[2]) == 1:
            self.channelButton3.configure(bg= "green")
            self.channelButton3.configure(text = "Channel ON")
        elif int(channel_buttons_config[2]) == 0:
            self.channelButton3.configure(bg= "purple")
            self.channelButton3.configure(text = "Timer ON")
        if int(channel_buttons_config[3]) == -1:
            self.channelButton4.configure(bg= "red")
            self.channelButton4.configure(text = "Channel OFF")
        elif int(channel_buttons_config[3]) == 1:
            self.channelButton4.configure(bg= "green")
            self.channelButton4.configure(text = "Channel ON")
        elif int(channel_buttons_config[3]) == 0:
            self.channelButton4.configure(bg= "purple")
            self.channelButton4.configure(text = "Timer ON")
        if int(channel_buttons_config[4]) == -1:
            self.channelButton5.configure(bg= "red")
            self.channelButton5.configure(text = "Channel OFF")
        elif int(channel_buttons_config[4]) == 1:
            self.channelButton5.configure(bg= "green")
            self.channelButton5.configure(text = "Channel ON")
        elif int(channel_buttons_config[4]) == 0:
            self.channelButton5.configure(bg= "purple")
            self.channelButton5.configure(text = "Timer ON")
        if int(channel_buttons_config[5]) == -1:
            self.channelButton6.configure(bg= "red")
            self.channelButton6.configure(text = "Channel OFF")
        elif int(channel_buttons_config[5]) == 1:
            self.channelButton6.configure(bg= "green")
            self.channelButton6.configure(text = "Channel ON")
        elif int(channel_buttons_config[5]) == 0:
            self.channelButton6.configure(bg= "purple")
            self.channelButton6.configure(text = "Timer ON")
        if int(channel_buttons_config[6]) == -1:
            self.channelButton7.configure(bg= "red")
            self.channelButton7.configure(text = "Channel OFF")
        elif int(channel_buttons_config[6]) == 1:
            self.channelButton7.configure(bg= "green")
            self.channelButton7.configure(text = "Channel ON")
        elif int(channel_buttons_config[6]) == 0:
            self.channelButton7.configure(bg= "purple")
            self.channelButton7.configure(text = "Timer ON")
        if int(channel_buttons_config[7]) == -1:
            self.channelButton8.configure(bg= "red")
            self.channelButton8.configure(text = "Channel OFF")
        elif int(channel_buttons_config[7]) == 1:
            self.channelButton8.configure(bg= "green")
            self.channelButton8.configure(text = "Channel ON")
        elif int(channel_buttons_config[7]) == 0:
            self.channelButton8.configure(bg= "purple")
            self.channelButton8.configure(text = "Timer ON")
        if int(channel_buttons_config[8]) == -1:
            self.channelButton9.configure(bg= "red")
            self.channelButton9.configure(text = "Channel OFF")
        elif int(channel_buttons_config[8]) == 1:
            self.channelButton9.configure(bg= "green")
            self.channelButton9.configure(text = "Channel ON")
        elif int(channel_buttons_config[8]) == 0:
            self.channelButton9.configure(bg= "purple")
            self.channelButton9.configure(text = "Timer ON")
        if int(channel_buttons_config[9]) == -1:
            self.channelButton10.configure(bg= "red")
            self.channelButton10.configure(text = "Channel OFF")
        elif int(channel_buttons_config[9]) == 1:
            self.channelButton10.configure(bg= "green")
            self.channelButton10.configure(text = "Channel ON")
        elif int(channel_buttons_config[9]) == 0:
            self.channelButton10.configure(bg= "purple")
            self.channelButton10.configure(text = "Timer ON")
        if int(channel_buttons_config[10]) == -1:
            self.channelButton11.configure(bg= "red")
            self.channelButton11.configure(text = "Channel OFF")
        elif int(channel_buttons_config[10]) == 1:
            self.channelButton11.configure(bg= "green")
            self.channelButton11.configure(text = "Channel ON")
        elif int(channel_buttons_config[10]) == 0:
            self.channelButton11.configure(bg= "purple")
            self.channelButton11.configure(text = "Timer ON")
        if int(channel_buttons_config[11]) == -1:
            self.channelButton12.configure(bg= "red")
            self.channelButton12.configure(text = "Channel OFF")
        elif int(channel_buttons_config[11]) == 1:
            self.channelButton12.configure(bg= "green")
            self.channelButton12.configure(text = "Channel ON")
        elif int(channel_buttons_config[11]) == 0:
            self.channelButton12.configure(bg= "purple")
            self.channelButton12.configure(text = "Timer ON")
        if int(channel_buttons_config[12]) == -1:
            self.channelButton13.configure(bg= "red")
            self.channelButton13.configure(text = "Channel OFF")
        elif int(channel_buttons_config[12]) == 1:
            self.channelButton13.configure(bg= "green")
            self.channelButton13.configure(text = "Channel ON")
        elif int(channel_buttons_config[12]) == 0:
            self.channelButton13.configure(bg= "purple")
            self.channelButton13.configure(text = "Timer ON")
        if int(channel_buttons_config[13]) == -1:
            self.channelButton14.configure(bg= "red")
            self.channelButton14.configure(text = "Channel OFF")
        elif int(channel_buttons_config[13]) == 1:
            self.channelButton14.configure(bg= "green")
            self.channelButton14.configure(text = "Channel ON")
        elif int(channel_buttons_config[13]) == 0:
            self.channelButton14.configure(bg= "purple")
            self.channelButton14.configure(text = "Timer ON")
        if int(channel_buttons_config[14]) == -1:
            self.channelButton15.configure(bg= "red")
            self.channelButton15.configure(text = "Channel OFF")
        elif int(channel_buttons_config[14]) == 1:
            self.channelButton15.configure(bg= "green")
            self.channelButton15.configure(text = "Channel ON")
        elif int(channel_buttons_config[14]) == 0:
            self.channelButton15.configure(bg= "purple")
            self.channelButton15.configure(text = "Timer ON")
        if int(channel_buttons_config[15]) == -1:
            self.channelButton16.configure(bg= "red")
            self.channelButton16.configure(text = "Channel OFF")
        elif int(channel_buttons_config[15]) == 1:
            self.channelButton16.configure(bg= "green")
            self.channelButton16.configure(text = "Channel ON")
        elif int(channel_buttons_config[15]) == 0:
            self.channelButton16.configure(bg= "purple")
            self.channelButton16.configure(text = "Timer ON")
        #fcns triggered by control button
    def channel_1(self):
        if int(channel_buttons_config[0]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton1.configure(bg= "green")
            self.channelButton1.configure(text = "Channel ON")
            channel_buttons_config[0] = 1
        elif int(channel_buttons_config[0]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton1.configure(bg= "purple")
            self.channelButton1.configure(text = "Timer ON")
            channel_buttons_config[0] = 0
        elif int(channel_buttons_config[0]) == 0:
            self.channelButton1.configure(bg= "red")
            self.channelButton1.configure(text = "Channel OFF")
            channel_buttons_config[0] = -1
        self.channel_buttons_save()
    def channel_2(self):
        if int(channel_buttons_config[1]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton2.configure(bg= "green")
            self.channelButton2.configure(text = "Channel ON")
            channel_buttons_config[1] = 1
        elif int(channel_buttons_config[1]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton2.configure(bg= "purple")
            self.channelButton2.configure(text = "Timer ON")
            channel_buttons_config[1] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[1]) == 0:
            self.channelButton2.configure(bg= "red")
            self.channelButton2.configure(text = "Channel OFF")
            channel_buttons_config[1] = -1
        self.channel_buttons_save()
    def channel_3(self):
        if int(channel_buttons_config[2]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton3.configure(bg= "green")
            self.channelButton3.configure(text = "Channel ON")
            channel_buttons_config[2] = 1
        elif int(channel_buttons_config[2]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton3.configure(bg= "purple")
            self.channelButton3.configure(text = "Timer ON")
            channel_buttons_config[2] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[2]) == 0:
            self.channelButton3.configure(bg= "red")
            self.channelButton3.configure(text = "Channel OFF")
            channel_buttons_config[2] = -1
        self.channel_buttons_save()
    def channel_4(self):
        if int(channel_buttons_config[3]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton4.configure(bg= "green")
            self.channelButton4.configure(text = "Channel ON")
            channel_buttons_config[3] = 1
        elif int(channel_buttons_config[3]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton4.configure(bg= "purple")
            self.channelButton4.configure(text = "Timer ON")
            channel_buttons_config[3] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[3]) == 0:
            self.channelButton4.configure(bg= "red")
            self.channelButton4.configure(text = "Channel OFF")
            channel_buttons_config[3] = -1
        self.channel_buttons_save()
    def channel_5(self):
        if int(channel_buttons_config[4]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton5.configure(bg= "green")
            self.channelButton5.configure(text = "Channel ON")
            channel_buttons_config[4] = 1
        elif int(channel_buttons_config[4]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton5.configure(bg= "purple")
            self.channelButton5.configure(text = "Timer ON")
            channel_buttons_config[4] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[4]) == 0:
            self.channelButton5.configure(bg= "red")
            self.channelButton5.configure(text = "Channel OFF")
            channel_buttons_config[4] = -1
        self.channel_buttons_save()
    def channel_6(self):
        if int(channel_buttons_config[5]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton6.configure(bg= "green")
            self.channelButton6.configure(text = "Channel ON")
            channel_buttons_config[5] = 1
        elif int(channel_buttons_config[5]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton6.configure(bg= "purple")
            self.channelButton6.configure(text = "Timer ON")
            channel_buttons_config[5] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[5]) == 0:
            self.channelButton6.configure(bg= "red")
            self.channelButton6.configure(text = "Channel OFF")
            channel_buttons_config[5] = -1
        self.channel_buttons_save()
    def channel_7(self):
        if int(channel_buttons_config[6]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton7.configure(bg= "green")
            self.channelButton7.configure(text = "Channel ON")
            channel_buttons_config[6] = 1
        elif int(channel_buttons_config[6]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton7.configure(bg= "purple")
            self.channelButton7.configure(text = "Timer ON")
            channel_buttons_config[6] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[6]) == 0:
            self.channelButton7.configure(bg= "red")
            self.channelButton7.configure(text = "Channel OFF")
            channel_buttons_config[6] = -1
        self.channel_buttons_save()
    def channel_8(self):
        if int(channel_buttons_config[7]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton8.configure(bg= "green")
            self.channelButton8.configure(text = "Channel ON")
            channel_buttons_config[7] = 1
        elif int(channel_buttons_config[7]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton8.configure(bg= "purple")
            self.channelButton8.configure(text = "Timer ON")
            channel_buttons_config[7] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[7]) == 0:
            self.channelButton8.configure(bg= "red")
            self.channelButton8.configure(text = "Channel OFF")
            channel_buttons_config[7] = -1
        self.channel_buttons_save()
    def channel_9(self):
        if int(channel_buttons_config[8]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton9.configure(bg= "green")
            self.channelButton9.configure(text = "Channel ON")
            channel_buttons_config[8] = 1
        elif int(channel_buttons_config[8]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton9.configure(bg= "purple")
            self.channelButton9.configure(text = "Timer ON")
            channel_buttons_config[8] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[8]) == 0:
            self.channelButton9.configure(bg= "red")
            self.channelButton9.configure(text = "Channel OFF")
            channel_buttons_config[8] = -1
        self.channel_buttons_save()
    def channel_10(self):
        if int(channel_buttons_config[9]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton10.configure(bg= "green")
            self.channelButton10.configure(text = "Channel ON")
            channel_buttons_config[9] = 1
        elif int(channel_buttons_config[9]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton10.configure(bg= "purple")
            self.channelButton10.configure(text = "Timer ON")
            channel_buttons_config[9] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[9]) == 0:
            self.channelButton10.configure(bg= "red")
            self.channelButton10.configure(text = "Channel OFF")
            channel_buttons_config[9] = -1
        self.channel_buttons_save()
    def channel_11(self):
        if int(channel_buttons_config[10]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton11.configure(bg= "green")
            self.channelButton11.configure(text = "Channel ON")
            channel_buttons_config[10] = 1
        elif int(channel_buttons_config[10]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton11.configure(bg= "purple")
            self.channelButton11.configure(text = "Timer ON")
            channel_buttons_config[10] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[10]) == 0:
            self.channelButton11.configure(bg= "red")
            self.channelButton11.configure(text = "Channel OFF")
            channel_buttons_config[10] = -1
        self.channel_buttons_save()
    def channel_12(self):
        if int(channel_buttons_config[11]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton12.configure(bg= "green")
            self.channelButton12.configure(text = "Channel ON")
            channel_buttons_config[11] = 1
        elif int(channel_buttons_config[11]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton12.configure(bg= "purple")
            self.channelButton12.configure(text = "Timer ON")
            channel_buttons_config[11] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[11]) == 0:
            self.channelButton12.configure(bg= "red")
            self.channelButton12.configure(text = "Channel OFF")
            channel_buttons_config[11] = -1
        self.channel_buttons_save()
    def channel_13(self):
        if int(channel_buttons_config[12]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton13.configure(bg= "green")
            self.channelButton13.configure(text = "Channel ON")
            channel_buttons_config[12] = 1
        elif int(channel_buttons_config[12]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton13.configure(bg= "purple")
            self.channelButton13.configure(text = "Timer ON")
            channel_buttons_config[12] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[12]) == 0:
            self.channelButton13.configure(bg= "red")
            self.channelButton13.configure(text = "Channel OFF")
            channel_buttons_config[12] = -1
        self.channel_buttons_save()
    def channel_14(self):
        if int(channel_buttons_config[13]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton14.configure(bg= "green")
            self.channelButton14.configure(text = "Channel ON")
            channel_buttons_config[13] = 1
        elif int(channel_buttons_config[13]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton14.configure(bg= "purple")
            self.channelButton14.configure(text = "Timer ON")
            channel_buttons_config[13] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[13]) == 0:
            self.channelButton14.configure(bg= "red")
            self.channelButton14.configure(text = "Channel OFF")
            channel_buttons_config[13] = -1
        self.channel_buttons_save()
    def channel_15(self):
        if int(channel_buttons_config[14]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton15.configure(bg= "green")
            self.channelButton15.configure(text = "Channel ON")
            channel_buttons_config[14] = 1
        elif int(channel_buttons_config[14]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton15.configure(bg= "purple")
            self.channelButton15.configure(text = "Timer ON")
            channel_buttons_config[14] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[14]) == 0:
            self.channelButton15.configure(bg= "red")
            self.channelButton15.configure(text = "Channel OFF")
            channel_buttons_config[14] = -1
        self.channel_buttons_save()
    def channel_16(self):
        if int(channel_buttons_config[15]) == -1:
        #change channel button color to green when channel is forced on
            self.channelButton16.configure(bg= "green")
            self.channelButton16.configure(text = "Channel ON")
            channel_buttons_config[15] = 1
        elif int(channel_buttons_config[15]) == 1:
        #change channel button color to purple to run on timer
            self.channelButton16.configure(bg= "purple")
            self.channelButton16.configure(text = "Timer ON")
            channel_buttons_config[15] = 0
        #change channel button color to red if channel is forced off
        elif int(channel_buttons_config[15]) == 0:
            self.channelButton16.configure(bg= "red")
            self.channelButton16.configure(text = "Channel OFF")
            channel_buttons_config[15] = -1
        self.channel_buttons_save()

#add settings page
class Settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Settings", bg='white', font = TITLE_FONT)
        label.pack(pady=10, padx=10)
        #navigation button
        navibutton1 = ttk.Button(self, text="Back to Dashboard",
                            command=lambda: controller.show_frame(HomePage))
        navibutton1.pack()
        navibutton2 = ttk.Button(self, text="Go to Control Panel",
                            command=lambda: controller.show_frame(ControlPanel))
        navibutton2.pack()
#add Video Stream page
class VideoStream(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Video Stream", bg='white', font = TITLE_FONT)
        label.pack(pady=10, padx=10)
        #navigation button
        navibutton1 = ttk.Button(self, text="Back to Dashboard",
                            command=lambda: controller.show_frame(HomePage))
        navibutton1.pack()
app = AllWindow()
app.geometry('1025x672')
#this makes app full screen, not sure if it's good for us or not
#app.attributes('-fullscreen', True)
#update animation first
ani = animation.FuncAnimation(f, animate, interval=5000)
#mainloop
app.mainloop()
