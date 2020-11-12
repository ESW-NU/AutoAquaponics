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
from sendtext import pCheck
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
param_list = ['pH', 'TDS (ppm)', 'Relative Humidity (%)', 'Air Temp (\N{DEGREE SIGN}C)', 'Water Temp (\N{DEGREE SIGN}C)', 'Distance (cm)']
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
                pCheck(float(config_settings[4][i]),float(config_settings[3][i]),key,current_param_val)
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
        
        # widget text
        widgets = ["pH", "TDS (ppm)", "DO (ppm)", "Phosphate (ppm)", "Nitrate (ppm)", "Ammonia (ppm)", "Air Temperature (\N{DEGREE SIGN}C)",
                   "Air Humidity (%)", "Water Temperature (\N{DEGREE SIGN}C)", "Water Level (cm)", "Flow Rate (GPH)"]
        # initialize entries list vars
        self.lower_entries = [0 for i in range(len(widgets))]
        self.upper_entries = [0 for i in range(len(widgets))]
        # initialize param vars
        pH_lower, TDS_lower, DO_lower, Phosphate_lower, Nitrate_lower, Ammonia_lower, Air_Temperature_lower, Air_Humidity_lower, \
            Water_Temperature_lower, Water_Level_lower, Flow_Rate_lower = [tk.DoubleVar() for x in range(len(widgets))]
        pH_upper, TDS_upper, DO_upper, Phosphate_upper, Nitrate_upper, Ammonia_upper, Air_Temperature_upper, Air_Humidity_upper, \
            Water_Temperature_upper, Water_Level_upper, Flow_Rate_upper = [tk.DoubleVar() for x in range(len(widgets))]
        # param var tables for looping
        widget_var_lower = [pH_lower, TDS_lower, DO_lower, Phosphate_lower, Nitrate_lower, Ammonia_lower, Air_Temperature_lower,
                            Air_Humidity_lower, Water_Temperature_lower, Water_Level_lower, Flow_Rate_lower]
        widget_var_upper = [pH_upper, TDS_upper, DO_upper, Phosphate_upper, Nitrate_upper, Ammonia_upper, Air_Temperature_upper,
                            Air_Humidity_upper, Water_Temperature_upper, Water_Level_upper, Flow_Rate_upper]
        
        # for each widget, create its upper and lower label and entry, store in temp var, then place in entries list
        for i in range(len(widgets)):
            lower_label = tk.Label(self,bg = 'white', width = 25, anchor = 'e', text="Min " + widgets[i] + ":")
            lower_label.grid(row=i+4, column = 1, padx = (0,10))
            lower_entry = tk.Entry(self, width = 20, textvariable = widget_var_lower[i])
            lower_entry.grid(row=i+4, column = 2, padx = (0,50))
            self.lower_entries[i] = lower_entry
            upper_label = tk.Label(self,bg = 'white', width = 25, anchor = 'e', text="Max " + widgets[i] + ":")
            upper_label.grid(row=i+4, column = 3, padx = (0,10))
            upper_entry = tk.Entry(self, width = 20, textvariable = widget_var_upper[i])
            upper_entry.grid(row=i+4, column = 4)
            self.upper_entries[i] = upper_entry

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
            upper_config = [round(float(entry.get()),2) for entry in self.upper_entries]  
            lower_config = [round(float(entry.get()),2) for entry in self.lower_entries]
            with open(config_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows([channel_buttons_config, on_config, off_config, upper_config, lower_config])
                file.flush()
        #destroy popup window after writing file
        self.popup.destroy()
        
    #fcn triggered by discard button
    def discard(self):
        #Delete current values
        for entry in self.lower_entries:  
            entry.delete(0, END)
        for entry in self.upper_entries:  
            entry.delete(0, END)
        #Get last saved values
        with open(config_path, "r") as file:
            config_settings = list(csv.reader(file))
            for entry in self.lower_entries:
                entry.insert(0, config_settings[3][i])
            for entry in self.upper_entries:
                entry.insert(0, config_settings[4][i])

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
