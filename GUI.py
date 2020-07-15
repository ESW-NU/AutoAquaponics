import datetime
import os
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
#animate function
f = Figure(figsize=(10,5), dpi=100)
plot1 = f.add_subplot(211)
plot2 = f.add_subplot(212)
#set file path
file_path = os.path.expanduser("~/Desktop/test.csv")
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
            tList.append(datetime.datetime.strptime(timedate, "%m/%d/%Y %H:%M:%S"))
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
    plot1.set_title("Aquaponic Sensors")
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
    plot1.autoscale(enable=False) #doesn't do anything now
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
        label = tk.Label(self, text="Dashboard", bg='white', font = TITLE_FONT)
        label.pack(pady=10, padx=10)
        #Updating text boxes showing latest water parameter
        #self.pHtext = tk.StringVar()
        #self.GetValues()
        #pHLevel = tk.Label(self, textvariable=self.pHtext, bg='white', font = TITLE_FONT)
        #pHLevel.place(x=20, y=30)
        #quit button
        quitButton = tk.Button(self, text="QUIT", fg='red',
                                command=quit)
        quitButton.pack()
        #navigation button
        navibutton1 = ttk.Button(self, text="Control Panel",
                            command=lambda: controller.show_frame(ControlPanel))
        navibutton1.pack()
        navibutton2 = ttk.Button(self, text="Settings",
                            command=lambda: controller.show_frame(Settings))
        navibutton2.pack()
        
        #bring up canvas
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand = True)
        #add navigation bar
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
#function to update live text, doesn't work yet
#    def GetValues(self):
#        pullData = open("/media/pi/68D2-7E93/test.csv","r").read()
#        dataList = pullData.split('\n')
#        for eachLine in dataList:
#            if len(eachLine) >1:
#                timedate, voltage, voltage1 = eachLine.split(',')
#                self.pHtext.set(str(voltage))

#add control panel page
class ControlPanel(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
    #text labels
        Title = tk.Label(self, text="Control Panel", bg= 'white', font = TITLE_FONT)
        Title.pack(pady=10, padx=10)
        ChannelTitle = tk.Label(self, text="Channel Overrides", bg='white', font = MEDIUM_FONT)
        ChannelTitle.place(x=108, y=90)
    #channel labels
        Channel_1 = tk.Label(self, text="1", bg='white', font = SMALL_FONT)
        Channel_1.place(x=38, y=122)
        Channel_2 = tk.Label(self, text="2", bg='white', font = SMALL_FONT)
        Channel_2.place(x=38, y=157)
        Channel_3 = tk.Label(self, text="3", bg='white', font = SMALL_FONT)
        Channel_3.place(x=38, y=192)
        Channel_4 = tk.Label(self, text="4", bg='white', font = SMALL_FONT)
        Channel_4.place(x=38, y=227)
        Channel_5 = tk.Label(self, text="5", bg='white', font = SMALL_FONT)
        Channel_5.place(x=38, y=262)
        Channel_6 = tk.Label(self, text="6", bg='white', font = SMALL_FONT)
        Channel_6.place(x=38, y=297)
        Channel_7 = tk.Label(self, text="7", bg='white', font = SMALL_FONT)
        Channel_7.place(x=38, y=332)
        Channel_8 = tk.Label(self, text="8", bg='white', font = SMALL_FONT)
        Channel_8.place(x=38, y=367)
        Channel_9 = tk.Label(self, text="9", bg='white', font = SMALL_FONT)
        Channel_9.place(x=283, y=122)
        Channel_10 = tk.Label(self, text="10", bg='white', font = SMALL_FONT)
        Channel_10.place(x=283, y=157)
        Channel_11 = tk.Label(self, text="11", bg='white', font = SMALL_FONT)
        Channel_11.place(x=283, y=192)
        Channel_12 = tk.Label(self, text="12", bg='white', font = SMALL_FONT)
        Channel_12.place(x=283, y=227)
        Channel_13 = tk.Label(self, text="13", bg='white', font = SMALL_FONT)
        Channel_13.place(x=283, y=262)
        Channel_14 = tk.Label(self, text="14", bg='white', font = SMALL_FONT)
        Channel_14.place(x=283, y=297)
        Channel_15 = tk.Label(self, text="15", bg='white', font = SMALL_FONT)
        Channel_15.place(x=283, y=332)
        Channel_16 = tk.Label(self, text="16", bg='white', font = SMALL_FONT)
        Channel_16.place(x=283, y=367)
    #relay control buttons
        #relays 1-8
        self.channelButton1 = tk.Button(self, text="Channel OFF",
                                        bg= "red", fg= "white",
                                        command=self.channel_1)
        self.channelButton1.place(x=50, y=115)
        self.channelButton2 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_2)
        self.channelButton2.place(x=50, y=150)
        self.channelButton3 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_3)
        self.channelButton3.place(x=50, y=185)
        self.channelButton4 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_4)
        self.channelButton4.place(x=50, y=220)
        self.channelButton5 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_5)
        self.channelButton5.place(x=50, y=255)
        self.channelButton6 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_6)
        self.channelButton6.place(x=50, y=290)
        self.channelButton7 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_7)
        self.channelButton7.place(x=50, y=325)
        self.channelButton8 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_8)
        self.channelButton8.place(x=50, y=360)
        #relays 9-16
        self.channelButton9 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_9)
        self.channelButton9.place(x=170, y=115)
        self.channelButton10 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_10)
        self.channelButton10.place(x=170, y=150)
        self.channelButton11 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_11)
        self.channelButton11.place(x=170, y=185)
        self.channelButton12 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_12)
        self.channelButton12.place(x=170, y=220)
        self.channelButton13 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_13)
        self.channelButton13.place(x=170, y=255)
        self.channelButton14 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_14)
        self.channelButton14.place(x=170, y=290)
        self.channelButton15 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_15)
        self.channelButton15.place(x=170, y=325)
        self.channelButton16 = tk.Button(self, text="Channel OFF",
                                         bg= "red", fg= "white",
                                         command=self.channel_16)
        self.channelButton16.place(x=170, y=360)
        
        #navigation button
        navibutton1 = ttk.Button(self, text="Back to Dashboard",
                            command=lambda: controller.show_frame(HomePage))
        navibutton1.pack()
        
        
        #fcns triggered by control button
        #fcn to turn LED on or off
    def channel_1(self):
        #if LED1.value == 0:
        #    LED1.value = 1
        if self.channelButton1.cget('bg') == "red":
        #change light button color
            self.channelButton1.configure(bg= "green")
            self.channelButton1.configure(text = "Channel ON")
        else:
            #LED1.value = 0
        #change light button color to red if light off
            self.channelButton1.configure(bg= "red")
            self.channelButton1.configure(text = "Channel OFF")
    def channel_2(self):
        if self.channelButton2.cget('bg') == "red":
        #change light button color
            self.channelButton2.configure(bg= "green")
            self.channelButton2.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton2.configure(bg= "red")
            self.channelButton2.configure(text = "Channel OFF")
    def channel_3(self):
        if self.channelButton3.cget('bg') == "red":
        #change light button color
            self.channelButton3.configure(bg= "green")
            self.channelButton3.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton3.configure(bg= "red")
            self.channelButton3.configure(text = "Channel OFF")
    def channel_4(self):
        if self.channelButton4.cget('bg') == "red":
        #change light button color
            self.channelButton4.configure(bg= "green")
            self.channelButton4.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton4.configure(bg= "red")
            self.channelButton4.configure(text = "Channel OFF")
    def channel_5(self):
        if self.channelButton5.cget('bg') == "red":
        #change light button color
            self.channelButton5.configure(bg= "green")
            self.channelButton5.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton5.configure(bg= "red")
            self.channelButton5.configure(text = "Channel OFF")
    def channel_6(self):
        if self.channelButton6.cget('bg') == "red":
        #change light button color
            self.channelButton6.configure(bg= "green")
            self.channelButton6.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton6.configure(bg= "red")
            self.channelButton6.configure(text = "Channel OFF")
    def channel_7(self):
        if self.channelButton7.cget('bg') == "red":
        #change light button color
            self.channelButton7.configure(bg= "green")
            self.channelButton7.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton7.configure(bg= "red")
            self.channelButton7.configure(text = "Channel OFF")
    def channel_8(self):
        if self.channelButton8.cget('bg') == "red":
        #change light button color
            self.channelButton8.configure(bg= "green")
            self.channelButton8.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton8.configure(bg= "red")
            self.channelButton8.configure(text = "Channel OFF")
    def channel_9(self):
        if self.channelButton9.cget('bg') == "red":
        #change light button color
            self.channelButton9.configure(bg= "green")
            self.channelButton9.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton9.configure(bg= "red")
            self.channelButton9.configure(text = "Channel OFF")
    def channel_10(self):
        if self.channelButton10.cget('bg') == "red":
        #change light button color
            self.channelButton10.configure(bg= "green")
            self.channelButton10.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton10.configure(bg= "red")
            self.channelButton10.configure(text = "Channel OFF")
    def channel_11(self):
        if self.channelButton11.cget('bg') == "red":
        #change light button color
            self.channelButton11.configure(bg= "green")
            self.channelButton11.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton11.configure(bg= "red")
            self.channelButton11.configure(text = "Channel OFF")
    def channel_12(self):
        if self.channelButton12.cget('bg') == "red":
        #change light button color
            self.channelButton12.configure(bg= "green")
            self.channelButton12.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton12.configure(bg= "red")
            self.channelButton12.configure(text = "Channel OFF")
    def channel_13(self):
        if self.channelButton13.cget('bg') == "red":
        #change light button color
            self.channelButton13.configure(bg= "green")
            self.channelButton13.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton13.configure(bg= "red")
            self.channelButton13.configure(text = "Channel OFF")
    def channel_14(self):
        if self.channelButton14.cget('bg') == "red":
        #change light button color
            self.channelButton14.configure(bg= "green")
            self.channelButton14.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton14.configure(bg= "red")
            self.channelButton14.configure(text = "Channel OFF")
    def channel_15(self):
        if self.channelButton15.cget('bg') == "red":
        #change light button color
            self.channelButton15.configure(bg= "green")
            self.channelButton15.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton15.configure(bg= "red")
            self.channelButton15.configure(text = "Channel OFF")
    def channel_16(self):
        if self.channelButton16.cget('bg') == "red":
        #change light button color
            self.channelButton16.configure(bg= "green")
            self.channelButton16.configure(text = "Channel ON")
        else:
        #change light button color to red if light off
            self.channelButton16.configure(bg= "red")
            self.channelButton16.configure(text = "Channel OFF")
            
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

        # ENTRY WIDGETS
        # pH widget
        pH_lower = DoubleVar()
        pH_upper = DoubleVar()
        self.pH_lower_label = Label(self,text="Lower limit pH:")
        self.pH_lower_entry = Entry(self,textvariable = pH_lower)
        self.pH_upper_label = Label(self,text="Upper limit pH:")
        self.pH_upper_entry = Entry(self,textvariable = pH_upper)
        self.pH_lower_label.place(x=200,y=100)
        self.pH_lower_entry.place(x=300,y=100)
        self.pH_upper_label.place(x=635,y=100)
        self.pH_upper_entry.place(x=735,y=100)
        # TDS widget
        TDS_lower = DoubleVar()
        TDS_upper = DoubleVar()
        self.TDS_lower_label = Label(self,text="Lower limit TDS (ppm):")
        self.TDS_lower_entry = Entry(self,textvariable = TDS_lower)
        self.TDS_upper_label = Label(self,text="Upper limit TDS (ppm):")
        self.TDS_upper_entry = Entry(self,textvariable = TDS_upper)
        self.TDS_lower_label.place(x=152,y=125)
        self.TDS_lower_entry.place(x=300,y=125)
        self.TDS_upper_label.place(x=587,y=125)
        self.TDS_upper_entry.place(x=735,y=125)
        # DO widget
        DO_lower = DoubleVar()
        DO_upper = DoubleVar()
        self.DO_lower_label = Label(self,text="Lower limit DO (ppm):")
        self.DO_lower_entry = Entry(self,textvariable = DO_lower)
        self.DO_upper_label = Label(self,text="Upper limit DO (ppm):")
        self.DO_upper_entry = Entry(self,textvariable = DO_upper)
        self.DO_lower_label.place(x=160,y=150)
        self.DO_lower_entry.place(x=300,y=150)
        self.DO_upper_label.place(x=594,y=150)
        self.DO_upper_entry.place(x=735,y=150)
        # Phosphate widget
        Phosphate_lower = DoubleVar()
        Phosphate_upper = DoubleVar()
        self.Phosphate_lower_label = Label(self,text="Lower limit Phosphate (ppm):")
        self.Phosphate_lower_entry = Entry(self,textvariable = Phosphate_lower)
        self.Phosphate_upper_label = Label(self,text="Upper limit Phosphate (ppm):")
        self.Phosphate_upper_entry = Entry(self,textvariable = Phosphate_upper)
        self.Phosphate_lower_label.place(x=115,y=175)
        self.Phosphate_lower_entry.place(x=300,y=175)
        self.Phosphate_upper_label.place(x=549,y=175)
        self.Phosphate_upper_entry.place(x=735,y=175)
        
        # Nitrate widget
        Nitrate_lower = DoubleVar()
        Nitrate_upper = DoubleVar()
        self.Nitrate_lower_label = Label(self,text="Lower limit Nitrate (ppm):")
        self.Nitrate_lower_entry = Entry(self,textvariable = Nitrate_lower)
        self.Nitrate_upper_label = Label(self,text="Upper limit Nitrate (ppm):")
        self.Nitrate_upper_entry = Entry(self,textvariable = Nitrate_upper)
        self.Nitrate_lower_label.place(x=138,y=200)
        self.Nitrate_lower_entry.place(x=300,y=200)
        self.Nitrate_upper_label.place(x=572,y=200)
        self.Nitrate_upper_entry.place(x=735,y=200)
        # Ammonia widget
        Ammonia_lower = DoubleVar()
        Ammonia_upper = DoubleVar()
        self.Ammonia_lower_label = Label(self,text="Lower limit Ammonia (ppm):")
        self.Ammonia_lower_entry = Entry(self,textvariable = Ammonia_lower)
        self.Ammonia_upper_label = Label(self,text="Upper limit Ammonia (ppm):")
        self.Ammonia_upper_entry = Entry(self,textvariable = Ammonia_upper)
        self.Ammonia_lower_label.place(x=123,y=225)
        self.Ammonia_lower_entry.place(x=300,y=225)
        self.Ammonia_upper_label.place(x=557,y=225)
        self.Ammonia_upper_entry.place(x=735,y=225)
        # Air Temperature widget
        Air_Temperature_lower = DoubleVar()
        Air_Temperature_upper = DoubleVar()
        self.Air_Temperature_lower_label = Label(self,text="Lower limit Air Temperature (celsius):")
        self.Air_Temperature_lower_entry = Entry(self,textvariable = Air_Temperature_lower)
        self.Air_Temperature_upper_label = Label(self,text="Upper limit Air Temperature (celsius):")
        self.Air_Temperature_upper_entry = Entry(self,textvariable = Air_Temperature_upper)
        self.Air_Temperature_lower_label.place(x=65,y=250)
        self.Air_Temperature_lower_entry.place(x=300,y=250)
        self.Air_Temperature_upper_label.place(x=500,y=250)
        self.Air_Temperature_upper_entry.place(x=735,y=250)
        # Air Humidity widget
        Air_Humidity_lower = DoubleVar()
        Air_Humidity_upper = DoubleVar()
        self.Air_Humidity_lower_label = Label(self,text="Lower limit Air Humidity (ppm):")
        self.Air_Humidity_lower_entry = Entry(self,textvariable = Air_Humidity_lower)
        self.Air_Humidity_upper_label = Label(self,text="Upper limit Air Humidity (ppm):")
        self.Air_Humidity_upper_entry = Entry(self,textvariable = Air_Humidity_upper)
        self.Air_Humidity_lower_label.place(x=105,y=275)
        self.Air_Humidity_lower_entry.place(x=300,y=275)
        self.Air_Humidity_upper_label.place(x=539,y=275)
        self.Air_Humidity_upper_entry.place(x=735,y=275)
        # Water Temperature widget
        Water_Temperature_lower = DoubleVar()
        Water_Temperature_upper = DoubleVar()
        self.Water_Temperature_lower_label = Label(self,text="Lower limit Water Temperature (celsius):")
        self.Water_Temperature_lower_entry = Entry(self,textvariable = Water_Temperature_lower)
        self.Water_Temperature_upper_label = Label(self,text="Upper limit Air Temperature (celsius):")
        self.Water_Temperature_upper_entry = Entry(self,textvariable = Water_Temperature_upper)
        self.Water_Temperature_lower_label.place(x=46,y=300)
        self.Water_Temperature_lower_entry.place(x=300,y=300)
        self.Water_Temperature_upper_label.place(x=500,y=300)
        self.Water_Temperature_upper_entry.place(x=735,y=300)
        # Water Level widget
        Water_Level_lower = DoubleVar()
        Water_Level_upper = DoubleVar()
        self.Water_Level_lower_label = Label(self,text="Lower limit Water Level (inches):")
        self.Water_Level_lower_entry = Entry(self,textvariable = Water_Level_lower)
        self.Water_Level_upper_label = Label(self,text="Upper limit Water Level (inches):")
        self.Water_Level_upper_entry = Entry(self,textvariable = Water_Level_upper) 
        self.Water_Level_lower_label.place(x=94,y=325)
        self.Water_Level_lower_entry.place(x=300,y=325)
        self.Water_Level_upper_label.place(x=528,y=325)
        self.Water_Level_upper_entry.place(x=735,y=325)
        # Flow Rate widget
        Flow_Rate_lower = DoubleVar()
        Flow_Rate_upper = DoubleVar()
        self.Flow_Rate_lower_label = Label(self,text="Lower limit Flow Rate (GPH):")
        self.Flow_Rate_lower_entry = Entry(self,textvariable = Flow_Rate_lower)
        self.Flow_Rate_upper_label = Label(self,text="Upper limit Flow Rate (GPH):")
        self.Flow_Rate_upper_entry = Entry(self,textvariable = Flow_Rate_upper) 
        self.Flow_Rate_lower_label.place(x=120,y=350)
        self.Flow_Rate_lower_entry.place(x=300,y=350)
        self.Flow_Rate_upper_label.place(x=553,y=350)
        self.Flow_Rate_upper_entry.place(x=735,y=350)

    
    # Save Button 
        def save_Entry_Widget():
            pH_lower_saved = pH_lower.get()
            pH_upper_saved = pH_upper.get()
            TDS_lower_saved = TDS_lower.get()
            TDS_upper_saved = TDS_upper.get()
            DO_lower_saved = DO_lower.get()
            DO_upper_saved = DO_upper.get()
            Phosphate_lower_saved = Phosphate_lower.get()
            Phosphate_upper_saved = Phosphate_upper.get()
            Nitrate_lower_saved = Nitrate_lower.get()
            Nitrate_upper_saved = Nitrate_upper.get()
            Ammonia_lower_saved = Ammonia_lower.get()
            Ammonia_upper_saved = Ammonia_upper.get()
            Air_Temperature_lower_saved = Air_Temperature_lower.get()
            Air_Temperature_upper_saved = Air_Temperature_upper.get()
            Air_Humidity_lower_saved = Air_Humidity_lower.get()
            Air_Humidity_upper_saved = Air_Humidity_upper.get()
            Water_Temperature_lower_saved = Water_Temperature_lower.get()
            Water_Temperature_upper_saved = Water_Temperature_upper.get()
            Water_Level_lower_saved = Water_Level_lower.get()
            Water_Level_upper_saved = Water_Level_upper.get()
            Flow_Rate_lower_saved = Flow_Rate_lower.get()
            Flow_Rate_upper_saved = Flow_Rate_upper.get()

            file = open("entrywidget.txt","w")
            file.write("pH Range:")
            file.write(str(pH_lower_saved))
            file.write(str(pH_lower_saved))
            file.write("TDS Range:")
            file.write(str(TDS_lower_saved))
            file.write(str(TDS_upper_saved))
            file.write("DO Range:")
            file.write(str(DO_lower_saved))
            file.write(str(DO_upper_saved))
            file.write("Phosphate Range:")
            file.write(str(Phosphate_lower_saved))
            file.write(str(Phosphate_upper_saved))
            file.write("Nitrate Range:")
            file.write(str(Nitrate_lower_saved))
            file.write(str(Nitrate_upper_saved))
            file.write("Ammonia Range:")
            file.write(str(Ammonia_lower_saved))
            file.write(str(Ammonia_upper_saved))
            file.write("Air Temperature Range:")
            file.write(str(Air_Temperature_lower_saved))
            file.write(str(Air_Temperature_upper_saved))
            file.write("Air Humidity Range:")
            file.write(str(Air_Humidity_lower_saved))
            file.write(str(Air_Humidity_upper_saved))
            file.write("Water Temperature Range:")
            file.write(str(Water_Temperature_lower_saved))
            file.write(str(Water_Temperature_upper_saved))
            file.write("Water Level Range:")
            file.write(str(Water_Level_lower_saved))
            file.write(str(Water_Level_upper_saved))
            file.write("Flow Rate Range Range:")
            file.write(str(DO_lower_saved))
            file.write(str(DO_upper_saved))
            file.close()
        
        self.save_button = Button(self,text="Save Settings",command=save_Entry_Widget())
        self.save_button.place(x=450, y=410)
        
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
ani = animation.FuncAnimation(f, animate, interval=1000)
#mainloop
app.mainloop()