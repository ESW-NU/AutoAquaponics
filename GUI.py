from data import Reader
from datetime import datetime 
from typing import Container
#import led info, replace with relay info
#from gpiozero import PWMLED
#LED1 = PWMLED(17)
#import tkinter for GUI
import tkinter as tk
from tkinter import ttk, W, LEFT, END
#font types
TITLE_FONT = ("Verdana", 14, 'bold')
LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)
#import stuff for graph
import csv
import matplotlib
from matplotlib import ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk 
matplotlib.use('TkAgg')
from matplotlib import figure
from matplotlib import dates as mdates
#import animation to make graph live
import matplotlib.animation as animation
from matplotlib import style
style.use("seaborn-darkgrid")
#import vertical scroll bar
from vertical_scroll_frame import VerticalScrolledFrame

from main import user_settings
config_path, db_path = user_settings()

#initialize channel_buttons_config, entry configs, and SQLite reader
db_name = 'sensor_testdb.db'
reader = Reader(db_path, db_name)

with open(config_path, "r") as file:
    config_settings = list(csv.reader(file))
    if len(config_settings) != 5:
        with open(config_path, 'w', newline='') as file:
            channel_buttons_config = [-1]*16
            on_config = [0]*16
            off_config = [0]*16
            upper_config = [0]*11
            lower_config = [0]*11
            writer = csv.writer(file)
            writer.writerows([channel_buttons_config,on_config,off_config, upper_config, lower_config])
            config_settings = [channel_buttons_config,on_config,off_config, upper_config, lower_config]
            file.flush()
    channel_buttons_config = config_settings[0]
    on_config = config_settings[1]
    off_config = config_settings[2]
    upper_config = config_settings[3]
    lower_config = config_settings[4]
#create figure for plots and set figure size/layout
f = figure.Figure(figsize=(8.6,17.5), dpi=100)
f.subplots_adjust(top=0.993, bottom=0.015, hspace=0.4)

param_dict = {}
param_list = ['pH', 'TDS (ppm)', 'Relative Humidity (%)', 'Air Temp (C)', 'Water Temp (C)', 'Distance']
#param_list = ['pH', 'Water Temp', 'Air Temp', 'Nitrate', 'TDS', 'DO', 'Ammonia', 'Phosphate', 'Humidity', 'Flow Rate', 'Water Level']
live_dict = {}
class Live_Text:
    def __init__(self, label):
        self.label = label
    
class Sensor_Plot:
    def __init__(self, plot, tList, x_ax, param, incoming_data, plot_color):
        self.plot = plot
        self.tList = tList
        self.x_ax = x_ax
        self.param = param
        self.incoming_data = incoming_data #<- graph is bound by incoming data and Data Summary Table displays most recent value 20 of them
        self.plot_color = plot_color #initially 'b' for all
        
    def make_plot(self):

        self.plot.clear()
        self.plot.set_xlabel('Time')
        self.plot.set_ylabel(self.param)
        # plot.set_ylim(ylim) #UNIQUE BUT HOW?

        self.x_ax.xaxis_date()
        self.x_ax.xaxis.set_major_formatter(mdates.DateFormatter('%I:%M:%S %p'))
        
        [tk.set_visible(True) for tk in self.x_ax.get_xticklabels()]
        [label.set_rotation(10) for label in self.x_ax.xaxis.get_ticklabels()] #slant the x axis tick labels for extra coolness

#        self.plot.set_xlim(self.tList[-2], self.tList[0])
        self.x_ax.set_xlim(self.tList[-2], self.tList[0]) 
        self.x_ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins = 4))
        
        self.plot.fill_between(self.tList, self.incoming_data, #where=(self.incoming_data > [0]*len(self.incoming_data))
                               facecolor=self.plot_color, edgecolor=self.plot_color, alpha=0.5) #blue @initilization


most_recent = reader.get_timeset(table="SensorData", num=20)
#print("most recent", most_recent)
reader.commit()       
for i, param in enumerate(param_list, 1): 
    tList = []
    most_recent_20 = []
    for j in range(len(most_recent)):
        time_f = datetime.strptime(most_recent[j][0], "%m/%d/%Y %H:%M:%S")
        tList.append(time_f)
        most_recent_20.append(most_recent[j][i])
    
    subplot = f.add_subplot(6, 2, i) #sharex?
    x_ax = f.get_axes()
    current_plot = Sensor_Plot(subplot, tList, x_ax[i-1], param, most_recent_20, 'b')      
    param_dict[param] = current_plot
    current_plot.make_plot()

    
###ANIMATE FUNCTION, REMOVE LAST ITEM FROM MOST_RECENT_2O LIST AND INSERT FRESHLY CALLED VALUE TO INDEX[1]
def animate(ii):
    most_recent = reader.get_timeset(table="SensorData", num=1)
    reader.commit()
    if most_recent != None:
        with open(config_path, "r") as file:
            config_settings = list(csv.reader(file))
        for i, key in enumerate(param_dict, 1):
            current_plot = param_dict[key]
            current_param_val = float(most_recent[0][i])
            current_text = live_dict[key]
            if current_param_val > float(config_settings[3][i]) or current_param_val < float(config_settings[4][i]):
                current_text.label.config(text=most_recent[0][i], fg="red", bg="white")
                current_plot.plot_color = 'r'
            else:
                current_text.label.config(text=most_recent[0][i], fg="black", bg="white")
                current_plot.plot_color = 'g'
            
            data_stream = current_plot.incoming_data
            time_stream = current_plot.tList
            data_stream.pop()
            time_stream.pop()
            data_stream.insert(0, most_recent[0][i])
            time_f = datetime.strptime(most_recent[0][0], "%m/%d/%Y %H:%M:%S")
            time_stream.insert(0, time_f)
            current_plot.make_plot()
            
           
#initialization
class AllWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #add title
        tk.Tk.wm_title(self, "AutoAquaponics")
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
        background = canvas.copy_from_bbox(f.bbox)
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
        #data table labels
        table_title = tk.Label(self, text="Data Summary", bg="white", font = LARGE_FONT)
        table_title.place(x=28, y=40)
        for i, param in enumerate(param_list): #tk.Label self refers to Homepage
            param_label = tk.Label(self, text=param, fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=18, height=1, anchor=W, justify=LEFT)
            param_label.place(x=5, y=65+22*i)

        for i, param in enumerate(param_list):
            loading_text = tk.Label(self, text="Loading", fg="black", bg="white",
                    font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                    width=5, height=1)
            loading_text.place(x=156, y=65+22*i)
            current_text = Live_Text(loading_text)
            live_dict[param] = current_text
        
channel_count = []
button_count = []
on_times = []
off_times = []
on_buttons = []
off_buttons = []
#add control panel page
class ControlPanel(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        #title
        tk.Label(self, text="Control Panel", bg="white", font=TITLE_FONT).grid(row=0, columnspan=14)

        #navigation button
        navibutton1 = ttk.Button(self, text="Back to Dashboard", command=lambda: controller.show_frame(HomePage))
        navibutton1.grid(row = 1, columnspan = 14)

        #Save button
        self.saveButton= ttk.Button(self, text="Save", command=self.popup)
        self.saveButton.grid(row=2, columnspan=14, pady=(0,0))
        #Discard button
        self.discardButton= ttk.Button(self, text="Discard", command=self.discard)
        self.discardButton.grid(row=3, columnspan=14, pady=(0,20))
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(13, weight=1)
        
        def preconfig_label(count: str):
            return tk.Label(self, text=count, bg='white', font=SMALL_FONT)
        for count in range(1, 17):
            channel_count.append(preconfig_label(str(count)))
    
        preconfig_button = tk.Button(self, text="Channel OFF", bg= "red", fg= "white", width=10, 
                           height=1, command=self.get_channel_state) #command will change state
        for count in range(16):
            button_count.append(preconfig_button)
        
        
        #Labels, buttons, and entries, oh my!
        for i in range(16):
            if i > 7 and i < 15:
                row = i - 4
                channel_count[i].grid(row=row, column=7, padx=(40,0))
                button_count[i].grid(row=row, column=8)
                tk.Label(self, text="Turn on for:", bg="white").grid(row=row, column=9)
                tk.Label(self, text="Turn off for:", bg="white").grid(row=row, column=11)
                on_element = (tk.Entry(self, width=10))
                on_buttons.append(on_element)
                on_element.grid(row=row, column=10) #on entry
                off_element = (tk.Entry(self, width=10))
                off_buttons.append(off_element)
                off_element.grid(row=row, column=12) #off entry
            elif i == 7:
                row = i + 4
                channel_count[i].grid(row=row, column=1, pady=(0,20))
                button_count[i].grid(row=row, column=2, pady=(0,20))
                tk.Label(self, text="Turn on for:", bg="white").grid(row=row, column=3, pady=(0,10))
                tk.Label(self, text="Turn off for:", bg="white").grid(row=row, column=5, pady=(0,10))
                on_element = (tk.Entry(self, width=10))
                on_buttons.append(on_element)
                on_element.grid(row=row, column=4, pady=(0,10)) #on entry
                off_element = (tk.Entry(self, width=10))
                off_buttons.append(off_element)
                off_element.grid(row=row, column=6, pady=(0,10)) #off entry
            elif i == 15:
                row = i - 4
                channel_count[i].grid(row=row, column=7, padx=(40,0), pady=(0,20))
                button_count[i].grid(row=row, column=8, pady=(0,20))
                tk.Label(self, text="Turn on for:", bg="white").grid(row=row, column=9, pady=(0,10))
                tk.Label(self, text="Turn off for:", bg="white").grid(row=row, column=11, pady=(0,10))
                on_element = (tk.Entry(self, width=10))
                on_buttons.append(on_element)
                on_element.grid(row=row, column=10, pady=(0,10)) #on entry
                off_element = (tk.Entry(self, width=10))
                off_buttons.append(off_element)
                off_element.grid(row=row, column=12, pady=(0,10)) #off entry
            else:
                row = i + 4
                channel_count[i].grid(row=row, column=1)
                button_count[i].grid(row=row, column=2)
                tk.Label(self, text="Turn on for:", bg="white").grid(row=row, column=3)
                tk.Label(self, text="Turn off for:", bg="white").grid(row=row, column=5)
                on_element = (tk.Entry(self, width=10))
                on_buttons.append(on_element)
                on_element.grid(row=row, column=4) #on entry
                off_element = (tk.Entry(self, width=10))
                off_buttons.append(off_element)
                off_element.grid(row=row, column=6) #off entry
        #Tells user what to input
        tk.Label(self, text="*Input Time in Hours", bg="white").grid(row=12, columnspan=14)
        
        self.discard()
        
        

    #fcn triggered by save button
    def popup(self):
        #get the input of all entries as a float value to the hundredth place
        self.popup = tk.Tk()
        self.popup.wm_title("Alert")
        label = ttk.Label(self.popup, text="Are you sure you want to save?", font=MEDIUM_FONT)
        label.grid(row=0, columnspan=14, pady=(10,20), padx = (5,5))
        YesB = ttk.Button(self.popup, text="YES", command = self.save)
        YesB.grid(row=1, column=1, padx =(23,10), pady = (0,10))
        NoB = ttk.Button(self.popup, text="NO", command = self.popup.destroy)
        NoB.grid(row=1, column=2, pady = (0,10))
        self.popup.mainloop()

    #triggered if user press YES in popup window    
    def save(self):
        for i in range(16):
            try:
                user_ON = int(on_buttons[i].get())
                on_times.append(user_ON)
            except ValueError:
                on_times.append(0) #if left blank, fill w/zeros
            except AttributeError:
                on_times.append(0) #if you put not Integers, fill w/zeros
        for i in range(16):
            try:
                user_OFF = int(off_buttons[i].get())
                off_times.append(user_OFF)
            except ValueError:
                off_times.append(0) #if left blank, fill w/zeros
            except AttributeError:
                off_times.append(0) #if you put noy Integers, fill w/zeros
        # save channel button settings
        with open(config_path, 'r', newline='') as file:
            config_settings = list(csv.reader(file))
            channel_buttons_config = config_settings[0]
            on_config = on_times
            off_config = off_times
            upper_config = config_settings[3]
            lower_config = config_settings[4]
            with open(config_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows([channel_buttons_config, on_config, off_config, upper_config, lower_config])
                file.flush()
        #destroy popup window after writing file
        self.popup.destroy()
        
    #fcn triggered by discard button
    def discard(self):
        #Get last saved values
        with open(config_path, "r") as file:
            config_settings = list(csv.reader(file))
            for i in range(16):
                channel_buttons_config[i] = config_settings[0][i]
                on_buttons[i].delete(0, END)
                off_buttons[i].delete(0, END)
                on_buttons[i].insert(0, config_settings[1][i])  
                off_buttons[i].insert(0, config_settings[2][i])
    
    def get_channel_state(self):
        #ugh, try......counter ??? what the fuck.
        # Make a button/channel class w/method get_channel_state
        
        for i in range(16):
            if int(channel_buttons_config[i]) == -1: #change channel button color to green when channel is forced on
                button_count[i].configure(bg= "green")
                button_count[i].configure(text = "Channel ON")
                channel_buttons_config[i] = 1
                continue

            elif int(channel_buttons_config[i]) == 1: #change channel button color to purple to run on timer
                button_count[i].configure(bg= "purple")
                button_count[i].configure(text = "Timer ON")
                channel_buttons_config[i] = 0
                continue
  
            else:
                button_count[i].configure(bg= "red")
                button_count[i].configure(text = "Channel OFF")
                channel_buttons_config[i] = -1
                continue

class Settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Settings", bg='white', font = TITLE_FONT)
        label.grid(row = 0, columnspan= 14)
        #navigation button
        navibutton1 = ttk.Button(self, text="Back to Dashboard",
                            command=lambda: controller.show_frame(HomePage))
        navibutton1.grid(row = 1, columnspan = 14)
        #Save button
        self.saveButton= ttk.Button(self, text="Save", command=self.popup)
        self.saveButton.grid(row = 2, columnspan = 14)
        #Discard button
        self.discardButton= ttk.Button(self, text="Discard", command=self.discard)
        self.discardButton.grid(row = 3, columnspan = 14, pady = (0,20))


        # ENTRY WIDGETS      
        # pH widget
        pH_lower = tk.DoubleVar()
        pH_upper = tk.DoubleVar()
        # pH_lower = DoubleVar()
        # #pH_lower.set(??) <- need to set every value that is being put as some float?
        # pH_upper = DoubleVar()
        self.pH_lower_label = tk.Label(self,bg = 'white', width = 25, anchor = 'e', text="Min pH:")
        self.pH_lower_entry = tk.Entry(self, width = 20, textvariable = pH_lower)
        self.pH_upper_label = tk.Label(self,bg = 'white', width = 25, anchor = 'e', text="Max pH:")
        self.pH_upper_entry = tk.Entry(self, width = 20, textvariable = pH_upper)
        self.pH_lower_label.grid(row=4, column = 1, padx = (0,10))
        self.pH_lower_entry.grid(row=4, column = 2, padx = (0,50))
        self.pH_upper_label.grid(row=4, column = 3, padx = (0,10))
        self.pH_upper_entry.grid(row=4, column = 4)
        # TDS widget
        TDS_lower = tk.DoubleVar()
        TDS_upper = tk.DoubleVar()
        self.TDS_lower_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e',text="Min TDS (ppm):")
        self.TDS_lower_entry = tk.Entry(self, width = 20, textvariable = TDS_lower)
        self.TDS_upper_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e',text="Max TDS (ppm):")
        self.TDS_upper_entry = tk.Entry(self, width = 20, textvariable = TDS_upper)
        self.TDS_lower_label.grid(row=5, column = 1, padx = (0,10))
        self.TDS_lower_entry.grid(row=5, column = 2, padx = (0,50))
        self.TDS_upper_label.grid(row=5, column = 3, padx = (0,10))
        self.TDS_upper_entry.grid(row=5, column = 4)
        # DO widget
        DO_lower = tk.DoubleVar()
        DO_upper = tk.DoubleVar()
        self.DO_lower_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e',text="Min DO (ppm):")
        self.DO_lower_entry = tk.Entry(self, width = 20, textvariable = DO_lower)
        self.DO_upper_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e',text="Max DO (ppm):")
        self.DO_upper_entry = tk.Entry(self, width = 20, textvariable = DO_upper)
        self.DO_lower_label.grid(row=6, column = 1, padx = (0,10))
        self.DO_lower_entry.grid(row=6, column = 2, padx = (0,50))
        self.DO_upper_label.grid(row=6, column = 3, padx = (0,10))
        self.DO_upper_entry.grid(row=6, column = 4)
        # Phosphate widget
        Phosphate_lower = tk.DoubleVar()
        Phosphate_upper = tk.DoubleVar()
        self.Phosphate_lower_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e',text="Min Phosphate (ppm):")
        self.Phosphate_lower_entry = tk.Entry(self, width = 20, textvariable = Phosphate_lower)
        self.Phosphate_upper_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e',text="Max Phosphate (ppm):")
        self.Phosphate_upper_entry = tk.Entry(self, width = 20, textvariable = Phosphate_upper)
        self.Phosphate_lower_label.grid(row=7, column = 1, padx = (0,10))
        self.Phosphate_lower_entry.grid(row=7, column = 2, padx = (0,50))
        self.Phosphate_upper_label.grid(row=7, column = 3, padx = (0,10))
        self.Phosphate_upper_entry.grid(row=7, column = 4)
        
        # Nitrate widget
        Nitrate_lower = tk.DoubleVar()
        Nitrate_upper = tk.DoubleVar()
        self.Nitrate_lower_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e',text="Min Nitrate (ppm):")
        self.Nitrate_lower_entry = tk.Entry(self, width = 20, textvariable = Nitrate_lower)
        self.Nitrate_upper_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e',text="Max Nitrate (ppm):")
        self.Nitrate_upper_entry = tk.Entry(self, width = 20, textvariable = Nitrate_upper)
        self.Nitrate_lower_label.grid(row=8, column = 1, padx = (0,10))
        self.Nitrate_lower_entry.grid(row=8, column = 2, padx = (0,50))
        self.Nitrate_upper_label.grid(row=8, column = 3, padx = (0,10))
        self.Nitrate_upper_entry.grid(row=8, column = 4)
        # Ammonia widget
        Ammonia_lower = tk.DoubleVar()
        Ammonia_upper = tk.DoubleVar()
        self.Ammonia_lower_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e',text="Min Ammonia (ppm):")
        self.Ammonia_lower_entry = tk.Entry(self, width = 20, textvariable = Ammonia_lower)
        self.Ammonia_upper_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e',text="Max Ammonia (ppm):")
        self.Ammonia_upper_entry = tk.Entry(self, width = 20, textvariable = Ammonia_upper)
        self.Ammonia_lower_label.grid(row=9, column = 1, padx = (0,10))
        self.Ammonia_lower_entry.grid(row=9, column = 2, padx = (0,50))
        self.Ammonia_upper_label.grid(row=9, column = 3, padx = (0,10))
        self.Ammonia_upper_entry.grid(row=9, column = 4)
        # Air Temperature widget
        Air_Temperature_lower = tk.DoubleVar()
        Air_Temperature_upper = tk.DoubleVar()
        self.Air_Temperature_lower_label = tk.Label(self, bg = 'white', width = 25,anchor = 'e', text="Min Air Temperature (Celsius):")
        self.Air_Temperature_lower_entry = tk.Entry(self, width = 20, textvariable = Air_Temperature_lower)
        self.Air_Temperature_upper_label = tk.Label(self, bg = 'white', width = 25,anchor = 'e', text="Max Air Temperature (Celsius):")
        self.Air_Temperature_upper_entry = tk.Entry(self, width = 20, textvariable = Air_Temperature_upper)
        self.Air_Temperature_lower_label.grid(row=10, column = 1, padx = (0,10))
        self.Air_Temperature_lower_entry.grid(row=10, column = 2, padx = (0,50))
        self.Air_Temperature_upper_label.grid(row=10, column = 3, padx = (0,10))
        self.Air_Temperature_upper_entry.grid(row=10, column = 4)
        # Air Humidity widget
        Air_Humidity_lower = tk.DoubleVar()
        Air_Humidity_upper = tk.DoubleVar()
        self.Air_Humidity_lower_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e', text="Min Air Humidity (%):")
        self.Air_Humidity_lower_entry = tk.Entry(self, width = 20, textvariable = Air_Humidity_lower)
        self.Air_Humidity_upper_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e', text="Max Air Humidity (%):")
        self.Air_Humidity_upper_entry = tk.Entry(self, width = 20, textvariable = Air_Humidity_upper)
        self.Air_Humidity_lower_label.grid(row=11, column = 1, padx = (0,10))
        self.Air_Humidity_lower_entry.grid(row=11, column = 2, padx = (0,50))
        self.Air_Humidity_upper_label.grid(row=11, column = 3, padx = (0,10))
        self.Air_Humidity_upper_entry.grid(row=11, column = 4)
        # Water Temperature widget
        Water_Temperature_lower = tk.DoubleVar()
        Water_Temperature_upper = tk.DoubleVar()
        self.Water_Temperature_lower_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e', text="Min Water Temperature (Celsius):")
        self.Water_Temperature_lower_entry = tk.Entry(self, width = 20, textvariable = Water_Temperature_lower)
        self.Water_Temperature_upper_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e', text="Max Water Temperature (Celsius):")
        self.Water_Temperature_upper_entry = tk.Entry(self, width = 20, textvariable = Water_Temperature_upper)
        self.Water_Temperature_lower_label.grid(row=12, column = 1, padx = (0,10))
        self.Water_Temperature_lower_entry.grid(row=12, column = 2, padx = (0,50))
        self.Water_Temperature_upper_label.grid(row=12, column = 3, padx = (0,10))
        self.Water_Temperature_upper_entry.grid(row=12, column = 4)
        # Water Level widget
        Water_Level_lower = tk.DoubleVar()
        Water_Level_upper = tk.DoubleVar()
        self.Water_Level_lower_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e', text="Min Water Level (inches):")
        self.Water_Level_lower_entry = tk.Entry(self, width = 20, textvariable = Water_Level_lower)
        self.Water_Level_upper_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e', text="Max Water Level (inches):")
        self.Water_Level_upper_entry = tk.Entry(self, width = 20, textvariable = Water_Level_upper) 
        self.Water_Level_lower_label.grid(row=13, column = 1, padx = (0,10))
        self.Water_Level_lower_entry.grid(row=13, column = 2, padx = (0,50))
        self.Water_Level_upper_label.grid(row=13, column = 3, padx = (0,10))
        self.Water_Level_upper_entry.grid(row=13, column = 4)
        # Flow Rate widget
        Flow_Rate_lower = tk.DoubleVar()
        Flow_Rate_upper = tk.DoubleVar()
        self.Flow_Rate_lower_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e', text="Min Flow Rate (GPH):")
        self.Flow_Rate_lower_entry = tk.Entry(self, width = 20, textvariable = Flow_Rate_lower)
        self.Flow_Rate_upper_label = tk.Label(self,bg = 'white', width = 25,anchor = 'e', text="Max Flow Rate (GPH):")
        self.Flow_Rate_upper_entry = tk.Entry(self, width = 20, textvariable = Flow_Rate_upper) 
        self.Flow_Rate_lower_label.grid(row=14, column = 1, padx = (0,10))
        self.Flow_Rate_lower_entry.grid(row=14, column = 2, padx = (0,50))
        self.Flow_Rate_upper_label.grid(row=14, column = 3, padx = (0,10))
        self.Flow_Rate_upper_entry.grid(row=14, column = 4)

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(5, weight=3)
        self.discard()
        #Tells user what to input
        tk.Label(self, text="*Enter Min/Max Values For The Specified Parameters", bg="white").grid(row=15, columnspan=14, pady=(10,0))

    def popup(self):
        #get the input of all entries as a float value to the hundredth place
        self.popup = tk.Tk()
        self.popup.wm_title("Alert")
        label = ttk.Label(self.popup, text="Are you sure you want to save?", font=MEDIUM_FONT)
        label.grid(row=0, columnspan=14, pady=(10,20), padx = (5,5))
        YesB = ttk.Button(self.popup, text="YES", command = self.save)
        YesB.grid(row=1, column=1, padx =(23,10), pady = (0,10))
        NoB = ttk.Button(self.popup, text="NO", command = self.popup.destroy)
        NoB.grid(row=1, column=2, pady = (0,10))
        self.popup.mainloop()
    #triggered if user press YES in popup window
    def save(self):
        with open(config_path, 'r', newline='') as file:
            config_settings = list(csv.reader(file))
            channel_buttons_config = config_settings[0]
            on_config = config_settings[1]
            off_config = config_settings[2]
            upper_config = [
                round(float(self.pH_upper_entry.get()),2), 
                round(float(self.TDS_upper_entry.get()),2),
                round(float(self.DO_upper_entry.get()),2), 
                round(float(self.Phosphate_upper_entry.get()),2), 
                round(float(self.Nitrate_upper_entry.get()),2), 
                round(float(self.Ammonia_upper_entry.get()),2), 
                round(float(self.Air_Temperature_upper_entry.get()),2), 
                round(float(self.Air_Humidity_upper_entry.get()),2),
                round(float(self.Water_Temperature_upper_entry.get()),2),
                round(float(self.Water_Level_upper_entry.get()),2),
                round(float(self.Flow_Rate_upper_entry.get()),2),
                ]
            lower_config = [
                round(float(self.pH_lower_entry.get()),2), 
                round(float(self.TDS_lower_entry.get()),2), 
                round(float(self.DO_lower_entry.get()),2),
                round(float(self.Phosphate_lower_entry.get()),2), 
                round(float(self.Nitrate_lower_entry.get()),2), 
                round(float(self.Ammonia_lower_entry.get()),2), 
                round(float(self.Air_Temperature_lower_entry.get()),2), 
                round(float(self.Air_Humidity_lower_entry.get()),2),
                round(float(self.Water_Temperature_lower_entry.get()),2),
                round(float(self.Water_Level_lower_entry.get()),2),
                round(float(self.Flow_Rate_lower_entry.get()),2),
                ]
            with open(config_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows([channel_buttons_config, on_config, off_config, upper_config, lower_config])
                file.flush()
        #destroy popup window after writing file
        self.popup.destroy()
        
    #fcn triggered by discard button
    def discard(self):
        #Delete current values
        self.pH_lower_entry.delete(0, END)
        self.TDS_lower_entry.delete(0, END)
        self.DO_lower_entry.delete(0, END)
        self.Phosphate_lower_entry.delete(0, END)
        self.Nitrate_lower_entry.delete(0, END)
        self.Ammonia_lower_entry.delete(0, END)
        self.Air_Temperature_lower_entry.delete(0, END)
        self.Air_Humidity_lower_entry.delete(0, END)
        self.Water_Level_lower_entry.delete(0, END)
        self.Water_Temperature_lower_entry.delete(0, END)
        self.Flow_Rate_lower_entry.delete(0, END)
        self.pH_upper_entry.delete(0, END)
        self.TDS_upper_entry.delete(0, END)
        self.DO_upper_entry.delete(0, END)
        self.Phosphate_upper_entry.delete(0, END)
        self.Nitrate_upper_entry.delete(0, END)
        self.Ammonia_upper_entry.delete(0, END)
        self.Air_Temperature_upper_entry.delete(0, END)
        self.Air_Humidity_upper_entry.delete(0, END)
        self.Water_Level_upper_entry.delete(0, END)
        self.Water_Temperature_upper_entry.delete(0, END)
        self.Flow_Rate_upper_entry.delete(0, END)
        #Get last saved values
        with open(config_path, "r") as file:
            config_settings = list(csv.reader(file))
            self.pH_upper_entry.insert(0, config_settings[3][0])
            self.TDS_upper_entry.insert(0, config_settings[3][1])
            self.DO_upper_entry.insert(0, config_settings[3][2])
            self.Phosphate_upper_entry.insert(0, config_settings[3][3])
            self.Nitrate_upper_entry.insert(0, config_settings[3][4])
            self.Ammonia_upper_entry.insert(0, config_settings[3][5])
            self.Air_Temperature_upper_entry.insert(0, config_settings[3][6])
            self.Air_Humidity_upper_entry.insert(0, config_settings[3][7])
            self.Water_Temperature_upper_entry.insert(0, config_settings[3][8])
            self.Water_Level_upper_entry.insert(0, config_settings[3][9])
            self.Flow_Rate_upper_entry.insert(0, config_settings[3][10])
            
            self.pH_lower_entry.insert(0, config_settings[4][0])
            self.TDS_lower_entry.insert(0, config_settings[4][1])
            self.DO_lower_entry.insert(0, config_settings[4][2])
            self.Phosphate_lower_entry.insert(0, config_settings[4][3])
            self.Nitrate_lower_entry.insert(0, config_settings[4][4])
            self.Ammonia_lower_entry.insert(0, config_settings[4][5])
            self.Air_Temperature_lower_entry.insert(0, config_settings[4][6])
            self.Air_Humidity_lower_entry.insert(0, config_settings[4][7])
            self.Water_Temperature_lower_entry.insert(0, config_settings[4][8])
            self.Water_Level_lower_entry.insert(0, config_settings[4][9])
            self.Flow_Rate_lower_entry.insert(0, config_settings[4][10])

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
