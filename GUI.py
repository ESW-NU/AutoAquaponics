from typing import Optional
from data import Reader
from datetime import datetime 
#import tkinter for GUI
import tkinter as tk
from tkinter import ttk, W, LEFT, END
#initializations for video
from PIL import Image, ImageTk
'''import cv2   #open source computer vision library
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)'''
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
from sendtext import allOk
from main import user_settings
config_path, db_path, img_path = user_settings()


#initialize entry configs, email_config, num_config, provider_config, and SQLite reader
db_name = 'sensor_db.db'
reader = Reader(db_path, db_name)

num_contacts = 5
with open(config_path, "r") as file:
    config_settings = list(csv.reader(file))
    if len(config_settings) != 8:
        with open(config_path, 'w', newline='') as file:
            enable_text = [str(False)]
            num_config = ['Enter Phone Number Here:']*num_contacts
            provider_config = ['']*num_contacts
            email_config = ['Email']*num_contacts
            upper_config = [1000]*11
            lower_config = [0]*11
            pump_config = [0, 0, None, "off"]
            oxygen_config = [0]
            writer = csv.writer(file)
            writer.writerows([enable_text,num_config,provider_config,email_config,upper_config, lower_config, pump_config, oxygen_config])
            config_settings = [enable_text,num_config,provider_config,email_config, upper_config, lower_config, pump_config, oxygen_config]
            file.flush()
    enable_text = config_settings[0]
    num_config = config_settings[1]
    provider_config = config_settings[2]
    email_config = config_settings[3]
    upper_config = config_settings[4]
    lower_config = config_settings[5]
    pump_config = config_settings[6]
    oxygen_config = config_settings[7]

#create figure for plots and set figure size/layout
#f = figure.Figure(figsize=(8.5,17.5), dpi=100)
f = figure.Figure(figsize=(10.2,10), dpi=100, facecolor='white')
#f.subplots_adjust(top=0.993, bottom=0.015, hspace=0.4)
f.subplots_adjust(top=0.993, bottom=0.015, left=0.04, right = 0.96, hspace=0.65)

param_dict = {}
param_list = ['pH', 'TDS (ppm)', 'Rela. Humidity (%)', 'Air Temp (\N{DEGREE SIGN}C)', 'Water Temp (\N{DEGREE SIGN}C)', 'Water Level (cm)']
param_ylim = [(5, 9), (0, 1500), (20, 80), (15, 35), (15, 35), (0, 61)]
#param_list = ['pH', 'Water Temp', 'Air Temp', 'Nitrate', 'TDS', 'DO', 'Ammonia', 'Phosphate', 'Humidity', 'Flow Rate', 'Water Level']
live_dict = {}


########################
#this is for texting

allIsGood = {}
minuta = {}
#minuta is used to make sure that you're not bombarded with texts
Minute = {}
for i in param_list:
    allIsGood[i] = True
    minuta[i] = None
    Minute[i] = None

########################


class Live_Text:
    def __init__(self, label):
        self.label = label
    
class Sensor_Plot:
    def __init__(self, plot, tList, x_ax, ylim, param, incoming_data, plot_color):
        self.plot = plot
        self.tList = tList
        self.x_ax = x_ax
        self.ylim = ylim
        self.param = param
        self.incoming_data = incoming_data #<- graph is bound by incoming data and Data Summary Table displays most recent value 20 of them
        self.plot_color = plot_color #initially 'b' for all
        
    def make_plot(self):
        self.plot.clear()
        self.plot.set_xlabel('Time')
        self.plot.set_ylabel(self.param)
        self.plot.set_ylim(self.ylim)

        self.x_ax.xaxis_date()
        self.x_ax.xaxis.set_major_formatter(mdates.DateFormatter('%I:%M:%S %p'))
        
        [tk.set_visible(True) for tk in self.x_ax.get_xticklabels()]
        [label.set_rotation(10) for label in self.x_ax.xaxis.get_ticklabels()] #slant the x axis tick labels for extra coolness

        if len(self.tList) > 4:
            self.x_ax.set_xlim(self.tList[-2], self.tList[0])
        self.x_ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins = 4))
        
        self.plot.fill_between(self.tList, self.incoming_data, #where=(self.incoming_data > [0]*len(self.incoming_data))
                               facecolor=self.plot_color, edgecolor=self.plot_color, alpha=0.5) #blue @initilization

def initialize_plots(): #intiailizes plots...
    global initialize_plots
    try:
        most_recent = reader.get_timeset(table="SensorData", num=30) #initializes plot up to 20 if possible if possible
        for i, param in enumerate(param_list, 1):
            tList = []
            most_recent_any_size = []
            for j in range(len(most_recent)):
                time_f = datetime.strptime(most_recent[j][0], "%m/%d/%Y %H:%M:%S")
                tList.append(time_f)
                most_recent_any_size.append(most_recent[j][i])

            subplot = f.add_subplot(6, 2, i)  # sharex?
            x_ax = f.get_axes()
            
            current_plot = Sensor_Plot(subplot, tList, x_ax[i-1], param_ylim[i-1], param, most_recent_any_size, 'b')
            param_dict[param] = current_plot
            current_plot.make_plot()
                    
    except: #if there is no data points available to plot, initialize the subplots
        for i, param in enumerate(param_list, 1):
            subplot = f.add_subplot(6, 2, i)
            x_ax = f.get_axes()
            current_plot = Sensor_Plot(subplot, [], x_ax[i-1], param_ylim[i-1], param, [], 'b')
            param_dict[param] = current_plot
            #current_plot.make_plot()    
    reader.commit()
    initialize_plots = _plots_initialized

def _plots_initialized(): #ensures plots only intialized once though!
    pass
initialize_plots()



###ANIMATE FUNCTION, REMOVE LAST ITEM FROM MOST_RECENT_ANY LIST AND INSERT FRESHLY CALLED VALUE TO BE FIRST IN LIST
def animate(ii):

    while True:
        most_recent_time_graphed = param_dict[param_list[0]] #first, pulls up first plot
        most_recent = reader.get_timeset(table="SensorData", num=1)
        reader.commit()         #if identical, do not animate
        #then checks that plot's time list
        if  (len(most_recent) == 0):
            break
        
        time_reader = datetime.strptime(most_recent[0][0], "%m/%d/%Y %H:%M:%S")
        if (len(most_recent_time_graphed.tList) != 0) and (time_reader == most_recent_time_graphed.tList[0]):
            for i, param in enumerate(param_list, 1):
                current_text = live_dict[param]
                current_text.label.config(text=most_recent[0][i], fg="black", bg="white")
            break #checks if the timestamp is exactly the same as prior, i.e. no new data points have been logged in this frame
        #do I have to add an else?
    
        else:
            with open(config_path, "r") as file: #ELSE: this is a new data point, so go ahead and plot it
                config_settings = list(csv.reader(file))
            for i, key in enumerate(param_dict, 1):
                current_plot = param_dict[key]
                current_param_val = float(most_recent[0][i])
                current_text = live_dict[key] #update to live text data summary
                if current_param_val > float(config_settings[4][i-1]) or current_param_val < float(config_settings[5][i-1]):
                    #only send text if enable_text is True
                    if config_settings[0] == [str(True)]:
                    ###sends text if new problem arises or every 5  minutes
                        if allIsGood[key] and Minute[key] == None:
                            print('new problem')
                            Minute[key] = datetime.now().minute
                            minuta[key] = Minute[key]
                            pCheck(float(config_settings[4][i-1]),float(config_settings[5][i-1]),key,current_param_val,config_settings[1],config_settings[2]) #uncomment to test emergency texts
                        elif allIsGood[key] == False and abs(Minute[key] - datetime.now().minute) % 5 == 0 and not (minuta[key] == datetime.now().minute):
                            print('same problem')
                            minuta[key] = datetime.now().minute
                            pCheck(float(config_settings[4][i-1]),float(config_settings[5][i-1]),key,current_param_val,config_settings[1],config_settings[2]) #uncomment to test emergency texts
                            #pass
                        
                        #setting the parameter to not ok
                        allIsGood[key] = False

                    current_text.label.config(text=most_recent[0][i], fg="red", bg="white")
                    current_plot.plot_color = 'r'
                
                else:
                    current_text.label.config(text=most_recent[0][i], fg="black", bg="white")
                    current_plot.plot_color = 'g'
                    
                    ###setting the parameter back to true and sending "ok" text 
                    if allIsGood[key] == False:
                        Minute[key] = None
                        allOk(key,config_settings[1],config_settings[2])
                        pass
                    
                    allIsGood[key] = True

                data_stream = current_plot.incoming_data
                time_stream = current_plot.tList
                data_stream.insert(0, most_recent[0][i])
                time_f = datetime.strptime(most_recent[0][0], "%m/%d/%Y %H:%M:%S")
                time_stream.insert(0, time_f)
                if len(data_stream) < 20: #graph updates, growing to show 20 points
                    current_plot.make_plot()
                else:                      #there are 20 points and more available, so animation occurs
                    data_stream.pop()
                    time_stream.pop()
                    current_plot.make_plot()
            break

                           
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
        for F in (HomePage, ControlPanel, Settings, VideoStream, Lights, WaterPump,
                    FishFeeder, SensorArray, Oxygenator, Backwashing):
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
        scframe.place(x=225, y=40)
        #bring up canvas with plot in the frame with vertical scroll bar
        canvas = FigureCanvasTkAgg(f, scframe.interior)
        #background = canvas.copy_from_bbox(f.bbox)
        canvas.draw()
        #create title label
        label = tk.Label(self, text="Dashboard", bg='white', font = TITLE_FONT)
        label.place(x=600, y=10)
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
                            width=16, height=1, anchor=W, justify=LEFT)
            param_label.place(x=5, y=65+22*i)

        for i, param in enumerate(param_list):
            loading_text = tk.Label(self, text="Loading", fg="black", bg="white",
                    font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                    width=7, height=1)
            loading_text.place(x=140, y=65+22*i)
            current_text = Live_Text(loading_text)
            live_dict[param] = current_text
'''        
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
        
        # centers the popup window
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()
        positionRight = int(self.popup.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popup.winfo_screenheight()/2 - popup_height/2 )
        self.popup.geometry("+{}+{}".format(positionRight, positionDown))
        

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
                continue '''

def csv_write(row_number, to_write):
    with open(config_path, 'r', newline='') as file:
            config_settings = list(csv.reader(file))
            config_settings[row_number] = to_write
            with open(config_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(config_settings)
                file.flush()

class Settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Settings", bg='white', font = TITLE_FONT)
        label.grid(row = 0, columnspan= 14, pady=10)
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
        self.sendtext_state = tk.IntVar() #variable to hold checkbutton state
        self.s = ttk.Style() #make a new style for checkbutton so bg can be white
        self.s.configure('New.TCheckbutton', background='white')
        self.textButton = ttk.Checkbutton(self, text="Enable Emergency Texts",
                                variable=self.sendtext_state, onvalue = 1, offvalue = 0, style='New.TCheckbutton', command=self.change_state)
        self.textButton.grid(row = 16, columnspan = 14, pady=(10,20))
        if enable_text == [str(True)]: #initialize state of checkbutton depending on enable_text value
            self.sendtext_state.set(1)
        else:
            self.sendtext_state.set(0)
        #Tells user what to input
        tk.Label(self, text="*Enter Min/Max Values For The Specified Parameters", bg="white").grid(row=15, columnspan=14, pady=(10,0))

        # ENTRY WIDGETS
        self.lower_entries = [0 for i in range(len(param_list))]
        self.lower_entries = [tk.DoubleVar() for x in range(len(param_list))]
        
        self.upper_entries = [0 for i in range(len(param_list))]
        self.upper_entries = [tk.DoubleVar() for x in range(len(param_list))]
        
        # for each widget, create its upper and lower label and entry, store in temp var, then place in entries list
        for i in range(len(param_list)):
            lower_label = tk.Label(self,bg = 'white', width = 25, anchor = 'e', text="Min " + param_list[i] + ":")
            lower_label.grid(row=i+4, column = 1, padx = (0,10), pady=(0,0))
            lower_entry = tk.Entry(self, width = 20, highlightthickness = 0, textvariable = self.lower_entries[i])
            lower_entry.grid(row=i+4, column = 2, padx = (0,50), pady=(0,0))
            self.lower_entries[i] = lower_entry
            upper_label = tk.Label(self,bg = 'white', width = 25, anchor = 'e', text="Max " + param_list[i] + ":")
            upper_label.grid(row=i+4, column = 3, padx = (0,10), pady=(0,0))
            upper_entry = tk.Entry(self, width = 20, highlightthickness = 0, textvariable = self.upper_entries[i])
            upper_entry.grid(row=i+4, column = 4, padx = (0,50), pady=(0,0))
            self.upper_entries[i] = upper_entry

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(5, weight=2)
        
        bottomFrame = tk.Frame(master=self, bg='white')
        bottomFrame.grid(row=17, columnspan=14, pady=10)
        
        self.phone_number = [0 for i in range(num_contacts)]
        self.phone_number = [tk.StringVar() for x in range(num_contacts)]
        self.phone_carrier = [0 for i in range(num_contacts)]
        self.phone_carrier = [tk.StringVar() for x in range(num_contacts)]
        self.carriers = ['AT&T', 'Sprint', 'T-Mobile', 'Verizon', 'Boost Mobile', 'Cricket',
                            'Metro PCS', 'Tracfone', 'U.S. Cellular', 'Virgin Mobile']
        self.options = []
        self.email = [0 for i in range(num_contacts)]
        self.email = [tk.StringVar() for x in range(num_contacts)]
        
        # WIDGETS FOR CONTACTS
        for ii in range(num_contacts):
        # emergency phone number entry boxes:    
            self.phone_label = tk.Label(master=bottomFrame, bg = 'white', width = 8, justify = 'right', anchor = 'w', text='Contact ' + str(ii+1) + ':')
            self.phone_label.grid(row = ii+20, column = 0, padx = (10,10), pady = (0,0))
            phone_entry = tk.Entry(master=bottomFrame, width = 15, textvariable = self.phone_number[ii])
            phone_entry.grid(row = ii+20, column = 1, sticky = 'e', padx = (0,40), pady = (0,0))
            self.phone_number[ii] = phone_entry
        # emergency phone carrier label/optionmenus:
            self.carrier_label = tk.Label(master=bottomFrame, bg = 'white', width = 11, anchor = 'w', text='Phone Carrier:')
            self.carrier_label.grid(row = ii+20, column = 2, sticky = 'w', padx = (0,10), pady = (0,0))
            self.v = self.phone_carrier[ii]
            carrier_entry = tk.OptionMenu(bottomFrame, self.v, *self.carriers)
            carrier_entry.config(width = 12, highlightthickness = 0)
            carrier_entry.grid(row = ii+20, column = 3, sticky = 'w', padx = (0,40), pady = (0,0))
            self.options.append(self.v) #keep list of the options
        # email address label/entry boxes:
            self.email_label = tk.Label(master=bottomFrame, bg = 'white', width = 5, anchor = 'e', text='Email:')
            self.email_label.grid(row = ii+20, column = 4, sticky = 'w', padx = (0,10), pady = (0,0))
            email_entry = tk.Entry(master=bottomFrame, width = 35, textvariable = self.email[ii])
            email_entry.grid(row = ii+20, column = 5, sticky = 'w', padx = (0,0), pady = (0,0))
            self.email[ii] = email_entry

        self.discard()

    def popup(self):
        #get the input of all entries as a float value to the hundredth place
        self.popup = tk.Tk()
        self.popup.wm_title("Alert")
        label = ttk.Label(self.popup, text="Are you sure you want to save?", font=MEDIUM_FONT)
        label.grid(row=0, columnspan=14, pady=(10,20), padx = (5,5))
        
        # centers the popup window
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()
        positionRight = int(self.popup.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popup.winfo_screenheight()/2 - popup_height/2 )
        self.popup.geometry("+{}+{}".format(positionRight, positionDown))
        
        YesB = ttk.Button(self.popup, text="YES", command = self.save)
        YesB.grid(row=1, column=1, padx =(23,10), pady = (0,10))
        NoB = ttk.Button(self.popup, text="NO", command = self.popup.destroy)
        NoB.grid(row=1, column=2, pady = (0,10))
        self.popup.mainloop()
    #triggered if user press YES in popup window
    def save(self):
        enable_text = [str(self.textButton.instate(['selected']))]
        num_config = [entry.get() for entry in self.phone_number]
        provider_config = [option.get() for option in self.options]
        email_config = [entry.get() for entry in self.email]
        upper_config = [round(float(entry.get()),2) for entry in self.upper_entries]  
        lower_config = [round(float(entry.get()),2) for entry in self.lower_entries]
        to_write = [enable_text, num_config, provider_config, email_config, upper_config, lower_config]
        for i, to_wr in enumerate(to_write):
            csv_write(i, to_wr)
        #destroy popup window after writing file
        self.popup.destroy()
        
    #fcn triggered by discard button
    def discard(self):
        #Delete current values
        for entry in self.phone_number:
            entry.delete(0,END)
        for entry in self.email:
            entry.delete(0,END)
        for entry in self.upper_entries:  
            entry.delete(0, END)
        for entry in self.lower_entries:  
            entry.delete(0, END)
        #Get last saved values
        with open(config_path, "r") as file:
            config_settings = list(csv.reader(file))
            for i, entry in enumerate(self.phone_number):
                entry.insert(0, config_settings[1][i])
            for i, option in enumerate(self.phone_carrier):
                option.set(config_settings[2][i])
            for i, entry in enumerate(self.email):
                entry.insert(0, config_settings[3][i])
            for i, entry in enumerate(self.upper_entries):
                entry.insert(0, config_settings[4][i])
            for i, entry in enumerate(self.lower_entries):
                entry.insert(0, config_settings[5][i])
            

    def submit(self):
        # submit the entered phone number & carrier to the emergency texts list
        # need to add senttext.py to GUI before this can function
        if len(self.phone_number.get()) != 10:
            self.num_popup = tk.Tk()
            self.num_popup.wm_title("Alert")
            label = ttk.Label(self.num_popup, text="Invalid phone number.", font=MEDIUM_FONT)
            label.grid(row=0, columnspan=14, pady=(10,20), padx = (5,5))
            okb = ttk.Button(self.num_popup, text="OK", command = self.num_popup.destroy)
            okb.grid(row=1, column=1, padx = (20,0), pady = (0,15))
            self.num_popup.mainloop()
        elif self.phone_carrier.get() == 'Select':
            self.car_popup = tk.Tk()
            self.car_popup.wm_title("Alert")
            label = ttk.Label(self.car_popup, text="  Choose a carrier.  ", font=MEDIUM_FONT)
            label.grid(row=0, columnspan=14, pady=(10,20), padx = (5,5))
            okb = ttk.Button(self.car_popup, text="OK", command = self.car_popup.destroy)
            okb.grid(row=1, column=1, padx = (20,0), pady = (0,15))
            self.car_popup.mainloop()
        else:
            # numbers[self.phone_number.get()] = self.phone_carrier.get()     <- once sendtext.py is in GUI
            self.phone_entry.delete(0, 'end')
            self.phone_carrier.set('Select')
            self.ent_popup = tk.Tk()
            self.ent_popup.wm_title("Alert")
            label = ttk.Label(self.ent_popup, text="Phone number entered.", font=MEDIUM_FONT)
            label.grid(row=0, columnspan=14, pady=(10,20), padx = (5,5))
            okb = ttk.Button(self.ent_popup, text="OK", command = self.ent_popup.destroy)
            okb.grid(row=1, column=1, padx = (20,0), pady = (0,15))
            self.ent_popup.mainloop()   
    
    #saves the checkbutton's new state into the CSV
    def change_state(self):
        enable_text = [str(self.textButton.instate(['selected']))]
        to_write = [enable_text, num_config, provider_config, email_config, upper_config, lower_config, pump_config, oxygen_config]
        for i, to_wr in enumerate(to_write):
            csv_write(i, to_wr)

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
'''
        #main label for showing the feed 
        self.imagel = tk.Label(self)
        self.imagel.pack(pady=10, padx=10)
        #initialize button with a picture
        frame = self.get_frame()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.imagel.imgtk = imgtk
        self.imagel.configure(image=imgtk)
        #button to turn video on and off
        self.toggle_button = tk.Button(self, text="Video OFF", bg= "red", fg= "white", width=10, 
                           height=1, command=self.toggle)
        self.toggle_button.pack(pady=10)
        self.update()
    def toggle(self):
        if self.toggle_button['bg']=='red':
            self.toggle_button.config(bg='green',text='Video ON')
            self.update()
        elif self.toggle_button['bg']=='green':
            self.toggle_button.configure(bg='red',text='Video OFF')
    def get_frame(self):
        """get a frame from the cam and return it."""
        ret, frame = cap.read()
        return frame
    def update(self):
        """update frames."""
        if self.toggle_button['bg']=='green':
            frame = self.get_frame()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.imagel.imgtk = imgtk
            self.imagel.configure(image=imgtk)
            self.imagel.after(15, self.update)'''
            
class ControlPanel(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #title
        tk.Label(self, text="Control Panel", bg="white", font=TITLE_FONT).pack(pady = 10)

        #Setup for lables and button images
        self.ctrl_panel_labels = ["Lights", "Water Pump", "Fish Feeder", "Sensor Array", "Oxygenator", 
                                  "Backwashing", "Back"] 
        self.icons = ["light.png", "water.png", "food.png",  "sensor.png", "oxygen.png", 
                                 "backwash.png", "back.png"]
        self.ctrl_panel_image = []
        
        for image in self.icons:
            self.ctrl_panel_image.append(tk.PhotoImage(file = img_path + image)) #create array of images using image path
        
        buttonFrame = tk.Frame(master=self, bg='white')
        buttonFrame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        i = 0
        j = 0
        for counter in range(7):
            buttonFrame.columnconfigure(i, weight=1, minsize=300)
            buttonFrame.rowconfigure(i, weight=1, minsize=100)
    
            frame = tk.Frame(master=buttonFrame)

            frame.grid(row=i, column=j, padx=2, pady=2, sticky="nsew")
            button = tk.Button(master=frame, text=self.ctrl_panel_labels[counter], image=self.ctrl_panel_image[counter], compound = tk.TOP)
            if(counter == 0):
                button = tk.Button(master=frame, text=self.ctrl_panel_labels[counter], image=self.ctrl_panel_image[counter], compound = tk.TOP, command=lambda: controller.show_frame(Lights))
            if(counter == 1):
                button = tk.Button(master=frame, text=self.ctrl_panel_labels[counter], image=self.ctrl_panel_image[counter], compound = tk.TOP, command=lambda: controller.show_frame(WaterPump))
            if(counter == 2):
                button = tk.Button(master=frame, text=self.ctrl_panel_labels[counter], image=self.ctrl_panel_image[counter], compound = tk.TOP, command=lambda: controller.show_frame(FishFeeder))
            if(counter == 3):
                button = tk.Button(master=frame, text=self.ctrl_panel_labels[counter], image=self.ctrl_panel_image[counter], compound = tk.TOP, command=lambda: controller.show_frame(SensorArray))
            if(counter == 4):
                button = tk.Button(master=frame, text=self.ctrl_panel_labels[counter], image=self.ctrl_panel_image[counter], compound = tk.TOP, command=lambda: controller.show_frame(Oxygenator))
            if(counter == 5):
                button = tk.Button(master=frame, text=self.ctrl_panel_labels[counter], image=self.ctrl_panel_image[counter], compound = tk.TOP, command=lambda: controller.show_frame(Backwashing))
            if(counter == 6):
                button = tk.Button(master=frame, text=self.ctrl_panel_labels[counter], image=self.ctrl_panel_image[counter], compound = tk.TOP, command=lambda: controller.show_frame(HomePage))
            button.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            j += 1
            if(j == 3):
                i += 1
                j = 0
                if(i == 2):
                    j = 1

class Lights(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #title
        tk.Label(self, text="Lights", bg="white", font=TITLE_FONT).grid(row=0, column=1, pady=(0,10))
        #shelf1
        tk.Label(self, text = "shelf 1", bg = "white", font = MEDIUM_FONT).grid(row=1, column=0, pady=(0,10))
        self.toggle1 = tk.Button(self, text="Light OFF", bg= "red",  width=10, 
                           height=1, command=self.toggle_a)
        self.toggle1.grid(row=1, column=1, pady=(0,10))
        self.timer1 = tk.Button(self, text="timer", bg= "white",  width=10, 
                           height=1, command=self.popup)
        self.timer1.grid(row=1, column=2, pady=(0,10))
        #shelf2
        tk.Label(self, text = "shelf 2", bg = "white", font = MEDIUM_FONT).grid(row=2, column=0, pady=(0,10))
        self.toggle2 = tk.Button(self, text="Light OFF", bg= "red",  width=10, 
                           height=1, command=self.toggle_b)
        self.toggle2.grid(row=2, column=1, pady=(0,10))
        self.timer2 = tk.Button(self, text="timer", bg= "white",  width=10, 
                           height=1, command=self.popup)
        self.timer2.grid(row=2, column=2, pady=(0,10))
        #fish tank
        tk.Label(self, text = "fish tank", bg = "white", font = MEDIUM_FONT).grid(row=3, column=0, pady=(0,10))
        self.toggle_tank = tk.Button(self, text="Light OFF", bg= "red",  width=10, 
                           height=1, command=self.toggle_c)
        self.toggle_tank.grid(row=3, column=1, pady=(0,10))
        self.timer_tank = tk.Button(self, text="timer", bg= "white",  width=10, 
                           height=1, command=self.popup)
        self.timer_tank.grid(row=3, column=2, pady=(0,10))
        #basking
        tk.Label(self, text = "basking", bg = "white", font = MEDIUM_FONT).grid(row=4, column=0, pady=(0,10))
        self.toggle_basking = tk.Button(self, text="Light OFF", bg= "red",  width=10, 
                           height=1, command=self.toggle_d)
        self.toggle_basking.grid(row=4, column=1, pady=(0,10))
        self.timer_basking = tk.Button(self, text="timer", bg= "white",  width=10, 
                           height=1, command=self.popup)
        self.timer_basking.grid(row=4, column=2, pady=(0,20))
        #back button to Alternate Control Panel
        self.back = tk.Button(self, text="Back", bg= "white",  width=10, 
                           height=1, command=lambda: controller.show_frame(ControlPanel))
        self.back.grid(row = 5, column = 0)

    # toggle... ; _ ; technically works but it'd definitely be better if tidied up
    def toggle_a(self):
        if self.toggle1['bg']=='red':
            self.toggle1.config(bg='green',text='Lights ON')
            self.update()
        elif self.toggle1['bg']=='green':
            self.toggle1.configure(bg='red',text='Lights OFF')
        self.update()
    def toggle_b(self):
        if self.toggle2['bg']=='red':
            self.toggle2.config(bg='green',text='Lights ON')
            self.update()
        elif self.toggle2['bg']=='green':
            self.toggle2.configure(bg='red',text='Lights OFF')
        self.update()
    def toggle_c(self):
        if self.toggle_tank['bg']=='red':
            self.toggle_tank.config(bg='green',text='Lights ON')
            self.update()
        elif self.toggle_tank['bg']=='green':
            self.toggle_tank.configure(bg='red',text='Lights OFF')
        self.update()
    def toggle_d(self):
        if self.toggle_basking['bg']=='red':
            self.toggle_basking.config(bg='green',text='Lights ON')
            self.update_basking()
        elif self.toggle_basking['bg']=='green':
            self.toggle_basking.configure(bg='red',text='Lights OFF')
        self.update()
    
    def popup(self):
        #get the input of all entries as a float value to the hundredth place
        self.popup = tk.Tk()
        self.popup.wm_title("Timer")
        start_label= ttk.Label(self.popup, text="Start", font=MEDIUM_FONT)
        start_entry = ttk.Entry(self.popup, width=10)
        duration_label = ttk.Label(self.popup, text="Duration", font=MEDIUM_FONT)
        duration_entry = ttk.Entry(self.popup, width=10)
        start_label.grid(row=0, column=0, pady=(0,10))
        duration_label.grid(row=1, column=0, pady=(0,10))
        start_entry.grid(row=0, column=1, pady=(0,10))
        duration_entry.grid(row=1, column=1, pady=(0,10))

        save_button = ttk.Button(self.popup, text="SAVE", command = self.save)
        save_button.grid(row=2, column=0, pady = (0,10))
        cancel_button = ttk.Button(self.popup, text="CANCEL", command = self.popup.destroy)
        cancel_button.grid(row=2, column=1, pady = (0,10))
        
        # centers the popup window
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()
        positionRight = int(self.popup.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popup.winfo_screenheight()/2 - popup_height/2 )
        self.popup.geometry("+{}+{}".format(positionRight, positionDown))
        self.popup.geometry('300x200')
        self.popup.mainloop()  
   
    #triggered if user press SAVE in popup window
    def save(self):
        # does something here
        #destroy popup window after writing file
        self.popup.destroy()

class WaterPump(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #title
        tk.Label(self, text="Water Pump", bg="white", font=TITLE_FONT).pack(pady = 10)
        #navigation button
        navibutton1 = tk.Button(self, text="Back", width=9, command=lambda: controller.show_frame(ControlPanel))
        navibutton1.pack(pady = (0,10))
        
        self.rateA, self.rateB, self.time = tk.IntVar(), tk.IntVar(), tk.IntVar()
        with open(config_path, 'r', newline='') as file:
            config_settings = list(csv.reader(file))
            pump_config = config_settings[6]
        self.rateA.set(pump_config[0])
        self.rateB.set(pump_config[1])
        self.time.set(pump_config[2])
        self.mode = pump_config[3]

        self.buttonFrame = tk.Frame(master=self, bg='white')
        self.buttonFrame.pack()
        tk.Label(master=self.buttonFrame, text="aaaaaaaaaaaaa", bg="white", fg="white").grid(row=1, column=0)
        tk.Label(master=self.buttonFrame, text="aaaaaaaaaaaaa", bg="white", fg="white").grid(row=1, column=3, columnspan=2)
        tk.Label(master=self.buttonFrame, text="Flow Control:", bg="white").grid(row=0, column=1, sticky="E")
        tk.Label(master=self.buttonFrame, text="Bed A Flow Rate (gal/hr):", bg="white").grid(row=1, column=1)
        tk.Label(master=self.buttonFrame, text="Bed B Flow Rate (gal/hr):", bg="white").grid(row=2, column=1)

        self.control = tk.Button(master=self.buttonFrame, text="OFF", fg="red", width=9, command=self.switch)
        self.control.grid(row=0, column=2, padx=5, pady=8)
        tk.Entry(master=self.buttonFrame, width=9, textvariable=self.rateA, bg="white").grid(row=1, column=2, padx=5, pady=5)
        tk.Entry(master=self.buttonFrame, width=9, textvariable=self.rateB, bg="white").grid(row=2, column=2, padx=5, pady=5)
        
        tk.Button(self, text="Save", width=9, command=self.popup).pack(pady = (10,0))

        if self.mode == "off":
            self.mode = "go to off"
        elif self.mode == "on":
            self.mode = "off"
        else:
            self.mode = "on"
        self.switch()

    def switch(self):
        if self.mode == "off":
            self.mode = "on"
            self.control.config(text="ON", fg="green")
        elif self.mode == "on":
            self.mode = "timer"
            self.control.config(text="Timer ON", fg="purple")
            self.mins = tk.Label(master=self.buttonFrame, text="(min):", bg = 'white')
            self.mins.grid(row=0, column=3)
            self.timer = tk.Entry(master=self.buttonFrame, width=4, textvariable=self.time)
            self.timer.grid(row=0, column=4, padx=(0,5), pady=5, columnspan=1)
        elif self.mode == "timer":
            self.mode = "off"
            self.control.config(text="OFF", fg="red")
            self.mins.destroy()
            self.timer.destroy()
        elif self.mode == "go to off":
            self.mode = "off"
            self.control.config(text="OFF", fg="red")
        with open(config_path, 'r', newline='') as file:
            config_settings = list(csv.reader(file))
            pump_config = [config_settings[6][0], config_settings[6][1], config_settings[6][2], self.mode]
        csv_write(6, pump_config)

    def popup(self):
        self.popup = tk.Tk()
        self.popup.wm_title("Alert")
        label = ttk.Label(self.popup, text="Are you sure you want to save?", font=MEDIUM_FONT)
        label.grid(row=0, columnspan=14, pady=(10,20), padx = (5,5))
        
        # centers the popup window
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()
        positionRight = int(self.popup.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popup.winfo_screenheight()/2 - popup_height/2 )
        self.popup.geometry("+{}+{}".format(positionRight, positionDown))
        
        YesB = ttk.Button(self.popup, text="YES", command = lambda:[self.save(), self.popup.destroy()])
        YesB.grid(row=1, column=1, padx =(23,10), pady = (0,10))
        NoB = ttk.Button(self.popup, text="NO", command = self.popup.destroy)
        NoB.grid(row=1, column=2, pady = (0,10))
        self.popup.mainloop()
    
    def save(self):
        if self.mode == "timer":
            real_time = self.timer.get()
        else:
            real_time = None
        pump_config = [self.rateA.get(), self.rateB.get(), real_time, self.mode]
        csv_write(6, pump_config)
        

class FishFeeder(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #title
        tk.Label(self, text="Fish Feeder", bg="white", font=TITLE_FONT).pack(pady = 10)
        #navigation button
        navibutton1 = ttk.Button(self, text="Back",
                            command=lambda: controller.show_frame(ControlPanel))
        navibutton1.pack()

class SensorArray(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #title
        tk.Label(self, text="Sensor Array", bg="white", font=TITLE_FONT).pack(pady = 10)
        #navigation button
        navibutton1 = ttk.Button(self, text="Back",
                            command=lambda: controller.show_frame(ControlPanel))
        navibutton1.pack()

class Oxygenator(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #title
        tk.Label(self, text="Oxygenator", bg="white", font=TITLE_FONT).pack(pady = 10)
        #navigation button
        navibutton1 = ttk.Button(self, text="Back", command=lambda: controller.show_frame(ControlPanel))
        navibutton1.pack(pady = (0,10))

        self.min = tk.IntVar()
        with open(config_path, 'r', newline='') as file:
            config_settings = list(csv.reader(file))
            oxygen_config = config_settings[7]
        self.min.set(oxygen_config[0])
        
        self.buttonFrame = tk.Frame(master=self, bg='white')
        self.buttonFrame.pack()
        tk.Label(master=self.buttonFrame, text="Current DO (ppm):", bg="white").grid(row=0, column=0)

        tk.Entry(master=self.buttonFrame, width=9, textvariable=self.min, bg="white").grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(self, text="Save", width=9, command=self.popup).pack(pady = (10,0))

    def popup(self):
        self.popup = tk.Tk()
        self.popup.wm_title("Alert")
        label = ttk.Label(self.popup, text="Are you sure you want to save?", font=MEDIUM_FONT)
        label.grid(row=0, columnspan=14, pady=(10,20), padx = (5,5))
        
        # centers the popup window
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()
        positionRight = int(self.popup.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popup.winfo_screenheight()/2 - popup_height/2 )
        self.popup.geometry("+{}+{}".format(positionRight, positionDown))
        
        YesB = ttk.Button(self.popup, text="YES", command = lambda:[self.save(), self.popup.destroy()])
        YesB.grid(row=1, column=1, padx =(23,10), pady = (0,10))
        NoB = ttk.Button(self.popup, text="NO", command = self.popup.destroy)
        NoB.grid(row=1, column=2, pady = (0,10))
        self.popup.mainloop()
    
    def save(self):
        csv_write(7, [self.min.get()])

class Backwashing(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #title
        tk.Label(self, text="Backwashing", bg="white", font=TITLE_FONT).pack(pady = 10)
        #navigation button
        navibutton1 = ttk.Button(self, text="Back",
                            command=lambda: controller.show_frame(ControlPanel))
        navibutton1.pack()

app = AllWindow()
#app.geometry('1025x672')
app.geometry('1280x623')
#this makes app full screen, not sure if it's good for us or not
#app.attributes('-fullscreen', True)
#update animation first
ani = animation.FuncAnimation(f, animate, interval=5000)
#mainloop
app.mainloop()
