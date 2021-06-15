from data import Reader
from DataLogger import all_we_got_now
import datetime, time
#import tkinter for GUI
import tkinter as tk
from tkinter import ttk, W, LEFT, END
#initializations for video
from PIL import Image, ImageTk

#uncomment later
import cv2   #open source computer vision library
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)

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

# returns the current csv in a 2D list, where list[i][j] is the jth element of the ith row of the list
def csv_read():
    with open(config_path, "r") as file:
        return list(csv.reader(file))

# given a row name string and list to write, replaces the given row with the new list
# make sure to give this function the row string exactly as it exists in the dictionary
# make sure the list to write is the proper length and contains the proper values
def csv_write(row_name, to_write):
    row_number = config_dict[row_name]
    with open(config_path, 'r', newline='') as file:
            config_settings = list(csv.reader(file))
            if len(config_settings) > row_number:
                config_settings[row_number] = to_write
            else:
                config_settings.append(to_write)
            with open(config_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(config_settings)
                file.flush()

#initialize entry configs, email_config, num_config, provider_config, and SQLite reader
db_name = 'sensor_db.db'
reader = Reader(db_path, db_name)
num_contacts = 5

# Enter row title here when adding a new row to the csv:
# Index can be any value, as long as 0 through (#rows-1) are present in the list of indices
config_dict = {
    'enable_text':0,
    'num_config':1,
    'provider_config':2,
    'email_config':3,
    'upper_config':4,
    'lower_config':5,
    'pump_config':6,
    'oxygen_config':7,
    'sensor_config':8,
    'lights_config':9
    }

# Enter row title here when adding a new row to the csv:
# Make sure to use the same title as was used in config_dict
# Enter the desired initialization as the dictionary value
init_dict = {
    'enable_text': [str(False)],
    'num_config': ['Enter Phone Number Here:']*num_contacts,
    'provider_config': ['']*num_contacts,
    'email_config': ['Email']*num_contacts,
    'upper_config': [1000]*11,
    'lower_config': [0]*11,
    'pump_config': [0, 0, None, "off"],
    'oxygen_config': [0],
    'sensor_config': ['off']*4,
    'lights_config': ['off']*4+[0]*8
}

# initializes csv, if not properly initialized
config_settings = csv_read()
if len(config_settings) != len(config_dict):
    for name in config_dict:
        csv_write(name, init_dict[name])
config_settings = csv_read()
enable_text = config_settings[config_dict['enable_text']]

#create figure for plots and set figure size/layout
#f = figure.Figure(figsize=(8.5,17.5), dpi=100)
f = figure.Figure(figsize=(16.6,15), dpi=100, facecolor='white')
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
        most_recent = reader.query_by_num(table="SensorData", num=30) #initializes plot up to 20 if possible if possible
        for i, param in enumerate(param_list, 1):
            tList = []
            most_recent_any_size = []
            for j in range(len(most_recent)):
                #time_f = datetime.strptime(most_recent[j][0], "%m/%d/%Y %H:%M:%S")
                time_f = datetime.datetime.fromtimestamp(most_recent[j][0])
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
        most_recent = reader.query_by_num(table="SensorData", num=1)
        reader.commit()         #if identical, do not animate
        #then checks that plot's time list
        if  (len(most_recent) == 0):
            break
        
        #time_reader = datetime.strptime(most_recent[0][0], "%m/%d/%Y %H:%M:%S")
        time_reader = datetime.datetime.fromtimestamp(most_recent[0][0])
        if (len(most_recent_time_graphed.tList) != 0) and (time_reader == most_recent_time_graphed.tList[0]):
            for i, param in enumerate(param_list, 1):
                current_text = live_dict[param]
                current_text.label.config(text=most_recent[0][i], fg="black", bg="white")
            break #checks if the timestamp is exactly the same as prior, i.e. no new data points have been logged in this frame
        #do I have to add an else?
    
        else:
            config_settings = csv_read()
            c0, c1, c2 = config_dict['enable_text'], config_dict['num_config'], config_dict['provider_config']
            c3, c4, c5 = config_dict['email_config'], config_dict['upper_config'], config_dict['lower_config']
            for i, key in enumerate(param_dict, 1):
                current_plot = param_dict[key]
                current_param_val = float(most_recent[0][i])
                current_text = live_dict[key] #update to live text data summary
                if current_param_val > float(config_settings[c4][i-1]) or current_param_val < float(config_settings[c5][i-1]):
                    #only send text if enable_text is True
                    if config_settings[c0] == [str(True)]:
                    ###sends text if new problem arises or every 5  minutes
                        if allIsGood[key] and Minute[key] == None:
                            print('new problem')
                            Minute[key] = datetime.now().minute
                            minuta[key] = Minute[key]
                            pCheck(float(config_settings[c4][i-1]),float(config_settings[c5][i-1]),key,current_param_val,config_settings[c1],config_settings[c2]) #uncomment to test emergency texts
                        elif allIsGood[key] == False and abs(Minute[key] - datetime.now().minute) % 5 == 0 and not (minuta[key] == datetime.now().minute):
                            print('same problem')
                            minuta[key] = datetime.now().minute
                            pCheck(float(config_settings[c4][i-1]),float(config_settings[c5][i-1]),key,current_param_val,config_settings[c1],config_settings[c2]) #uncomment to test emergency texts
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
                        allOk(key,config_settings[c1],config_settings[c2])
                        pass
                    
                    allIsGood[key] = True

                data_stream = current_plot.incoming_data
                time_stream = current_plot.tList
                data_stream.insert(0, most_recent[0][i])
                #time_f = datetime.strptime(most_recent[0][0], "%m/%d/%Y %H:%M:%S")
                time_f = datetime.datetime.fromtimestamp(most_recent[0][0])
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
        scframe.place(x=225, y=100)
        #bring up canvas with plot in the frame with vertical scroll bar
        canvas = FigureCanvasTkAgg(f, scframe.interior)
        #background = canvas.copy_from_bbox(f.bbox)
        canvas.draw()
        #create title label
        label = tk.Label(self, text="Dashboard", bg='white', font = TITLE_FONT)
        label.place(x=900, y=10)
        #export data button
        exportButton = ttk.Button(self, text="Export Selected Data",
                            command=self.popup)
        exportButton.place(x=884, y=45)
        #embed graph into canvas
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        #add navigation bar
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        #color variables
        #data table labels
        table_title = tk.Label(self, text="Data Summary", bg="white", font = LARGE_FONT)
        table_title.place(x=28, y=100)
        for i, param in enumerate(param_list): #tk.Label self refers to Homepage
            param_label = tk.Label(self, text=param, fg="black", bg="white",
                            font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                            width=16, height=1, anchor=W, justify=LEFT)
            param_label.place(x=5, y=125+22*i)

        for i, param in enumerate(param_list):
            loading_text = tk.Label(self, text="Loading", fg="black", bg="white",
                    font = MEDIUM_FONT, borderwidth = 2, relief = "ridge",
                    width=7, height=1)
            loading_text.place(x=140, y=125+22*i)
            current_text = Live_Text(loading_text)
            live_dict[param] = current_text
    
    def popup(self):
        # setup the popup here
        self.popup = tk.Toplevel() #dark magic that makes the checkbutton variables change, use instead of = tk.Tk()
        self.popup.wm_title("Export Data")
        label = ttk.Label(self.popup, text="Select Data to Export", font=MEDIUM_FONT)
        label.grid(row=0, columnspan=14, pady=(10,20), padx = (100,100))
        
        # centers the popup window
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()
        positionRight = int(self.popup.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popup.winfo_screenheight()/2 - popup_height/2 )
        self.popup.geometry("+{}+{}".format(positionRight, positionDown))
        
        # ENTRY WIDGETS
        self.label_list= ["Start date for exported data:","End date for exported data:","Save to path:"]
        self.instru_list = [tk.StringVar() for i in range(len(self.label_list))]

        # for each widget, create its label and entry, store in temp var, then place in entries list
        for i in range(len(self.label_list)):
            label = tk.Label(self.popup, width = 25, anchor = 'e', text=self.label_list[i])
            label.grid(row=i+4, column = 1, padx = (0,10), pady=(0,0))
            entry = tk.Entry(self.popup, width = 20, highlightthickness = 0, textvariable = self.instru_list[i])
            entry.grid(row=i+4, column = 2, padx = (0,50), pady=(0,0))
            self.instru_list[i] = entry
        self.instru_list[0].insert(0, '01/15/2021')
        self.instru_list[1].insert(0, '08/15/2021')
        # self.instru_list[0].insert(0, 'Ex. 01/15/2021')
        # self.instru_list[1].insert(0, 'Ex. 02/15/2021')
        self.instru_list[2].insert(0, '/home/pi/Desktop/data.csv') #C:\Users\billm\Desktop\data.csv

        # CHECKBUTTON WIDGETS
        self.state_list = [tk.IntVar() for i in range(len(param_list))] #variable to hold checkbutton state
        
        for i in range(len(self.state_list)):
            checkButton = tk.Checkbutton(self.popup, text="Include " + param_list[i],
                                    variable=self.state_list[i])
            checkButton.grid(row = len(self.label_list)+5+i, columnspan = 14, pady=(0,0))
        
        self.graph_var = tk.IntVar()
        graphButton = tk.Checkbutton(self.popup, text="Generate Plot",
                                    variable=self.graph_var, onvalue = 1, offvalue = 0)
        graphButton.grid(row=2*len(param_list)+6, column=1)

        self.csv_var = tk.IntVar()
        self.csvButton = tk.Checkbutton(self.popup, text="Export CSV",
                                    variable=self.csv_var, onvalue = 1, offvalue = 0)
        self.csvButton.grid(row=2*len(param_list)+6, column=2)

        # BUTTON WIDGET
        self.executeButton = ttk.Button(self.popup, text="Execute", command=self.execute)
        self.executeButton.grid(row=2*len(param_list)+7, columnspan=14, pady=(10,20), padx = (100,100))
        
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(5, weight=2)

        self.popup.mainloop()

    def execute(self): #this function export/graph specified data depending on user input in the popup
        entry_text = [entry.get() for entry in self.instru_list]
        checkButton_state = [state.get() for state in self.state_list]
        graphButton_state = self.graph_var.get()
        csvButton_state = self.csv_var.get()
        start = time.mktime(datetime.datetime.strptime(entry_text[0], "%m/%d/%Y").timetuple())
        end = time.mktime(datetime.datetime.strptime(entry_text[1], "%m/%d/%Y").timetuple())
        columns = ["unix_time"]

        for i in range(len(param_list)):
            if checkButton_state[i] == 1:
                columns.append(all_we_got_now[i+1]) #all_we_got_now is defined in DataLogger

        if csvButton_state == 1: #this part of the code saves the specified data as a csv
            data = reader.query_by_time(start, end, columns)
            with open(entry_text[2], 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(columns)
                writer.writerows(data)

        if graphButton_state == 1: #this part of the code plots the specified data on same figure
            x = reader.query_by_time(start, end, ["unix_time"])
            for i in range(len(x)):
                x[i] = datetime.datetime.fromtimestamp(x[i][0]).strftime('%Y-%m-%d %I:%M:%S %p') #uses local time, could be wonky
            fig, axes = matplotlib.pyplot.subplots(1,1)
            for i in range(1, len(columns)):
                y = reader.query_by_time(start, end, [columns[i]])
                axes.plot(x, y, label = [columns[i]])
                
            matplotlib.pyplot.legend(labels=columns[1:], bbox_to_anchor=(1.05, 1.0), loc='upper left')
            axes.set_title("Exported Data")
            axes.set_xlabel("Time")
            axes.xaxis.set_major_locator(mticker.MaxNLocator(nbins = 10))
            matplotlib.pyplot.xticks(rotation=45)
            fig.tight_layout() #add margin around so xlabel doesn't pop out
            matplotlib.pyplot.show()

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
        label.grid(row=0, columnspan=14, pady=(10,20), padx = (100,100))
        
        # centers the popup window
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()
        positionRight = int(self.popup.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popup.winfo_screenheight()/2 - popup_height/2 )
        self.popup.geometry("+{}+{}".format(positionRight, positionDown))
        
        YesB = ttk.Button(self.popup, text="YES", command = self.save)
        YesB.grid(row=1, column=1, padx =(100,10), pady = (0,10))
        NoB = ttk.Button(self.popup, text="NO", command = self.popup.destroy)
        NoB.grid(row=1, column=2, padx=(10,100), pady = (0,10))
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
        names = ['enable_text', 'num_config', 'provider_config', 'email_config', 'upper_config', 'lower_config']
        for i in range(len(to_write)):
            csv_write(names[i], to_write[i])
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
        config_settings = csv_read()
        for i, entry in enumerate(self.phone_number):
            entry.insert(0, config_settings[config_dict['num_config']][i])
        for i, option in enumerate(self.phone_carrier):
            option.set(config_settings[config_dict['provider_config']][i])
        for i, entry in enumerate(self.email):
            entry.insert(0, config_settings[config_dict['email_config']][i])
        for i, entry in enumerate(self.upper_entries):
            entry.insert(0, config_settings[config_dict['upper_config']][i])
        for i, entry in enumerate(self.lower_entries):
            entry.insert(0, config_settings[config_dict['lower_config']][i])
            

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
        csv_write('enable_text', enable_text)

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
            self.imagel.after(15, self.update)
            
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
        tk.Label(self, text="Lights", bg="white", font=TITLE_FONT).pack(pady=10)
        navibutton1 = ttk.Button(self, text="Back", command=lambda: controller.show_frame(ControlPanel))
        navibutton1.pack(pady = (0,10))
        self.buttonFrame = tk.Frame(master=self, bg='white')
        self.buttonFrame.pack()

        # initialize param text
        tk.Label(self.buttonFrame, text = "Shelf 1", bg = "white").grid(row=0, column=0)
        tk.Label(self.buttonFrame, text = "Shelf 2", bg = "white").grid(row=1, column=0)
        tk.Label(self.buttonFrame, text = "Fish Tank", bg = "white").grid(row=2, column=0)
        tk.Label(self.buttonFrame, text = "Basking", bg = "white").grid(row=3, column=0)
        
        # initialize param buttons
        self.tog1 = tk.Button(self.buttonFrame, text="OFF", fg="red", width=9, command=lambda: self.switch(0))
        self.tog2 = tk.Button(self.buttonFrame, text="OFF", fg="red", width=9, command=lambda: self.switch(1))
        self.togTank = tk.Button(self.buttonFrame, text="OFF", fg="red", width=9, command=lambda: self.switch(2))
        self.togBask = tk.Button(self.buttonFrame, text="OFF", fg="red", width=9, command=lambda: self.switch(3))
        self.tog1.grid(row=0, column=1, padx=5, pady=8)
        self.tog2.grid(row=1, column=1, padx=5, pady=8)
        self.togTank.grid(row=2, column=1, padx=5, pady=8)
        self.togBask.grid(row=3, column=1, padx=5, pady=8)

        # initialize timer buttons
        self.time1 = tk.Button(self.buttonFrame, text="Timer", fg="purple", width=9, command=self.pop1)
        self.time2 = tk.Button(self.buttonFrame, text="Timer", fg="purple", width=9, command=self.pop2)
        self.timeTank = tk.Button(self.buttonFrame, text="Timer", fg="purple", width=9, command=self.popTank)
        self.timeBask = tk.Button(self.buttonFrame, text="Timer", fg="purple", width=9, command=self.popBask)
        self.time1.grid(row=0, column=2, padx=5, pady=8)
        self.time2.grid(row=1, column=2, padx=5, pady=8)
        self.timeTank.grid(row=2, column=2, padx=5, pady=8)
        self.timeBask.grid(row=3, column=2, padx=5, pady=8)

        # intialize param buttons to proper state based on current csv value
        for i in range(4):
            lights_config = csv_read()[config_dict['lights_config']]
            if lights_config[i] == "on":
                lights_config[i] = "off"
                csv_write('lights_config', lights_config)
                self.switch(i)
        
    # given a param index, switches its csv value and button text (between 'on'/'off')
    def switch(self, i):
        lights_config = csv_read()[config_dict['lights_config']]
        if lights_config[i] == "off":
            lights_config[i] = "on"
            if i == 0:
                self.tog1.config(text="ON", fg="green")
            elif i == 1:
                self.tog2.config(text="ON", fg="green")
            elif i == 2:
                self.togTank.config(text="ON", fg="green")
            elif i == 3:
                self.togBask.config(text="ON", fg="green")
        else:
            lights_config[i] = "off"
            if i == 0:
                self.tog1.config(text="OFF", fg="red")
            elif i == 1:
                self.tog2.config(text="OFF", fg="red")
            elif i == 2:
                self.togTank.config(text="OFF", fg="red")
            elif i == 3:
                self.togBask.config(text="OFF", fg="red")
        csv_write('lights_config', lights_config)

    # shelf 1 popup window: for setting start and duration times
    def pop1(self):
        self.pop1 = tk.Tk()
        self.pop1.wm_title("Shelf 1")
        popup_width = self.pop1.winfo_reqwidth()
        popup_height = self.pop1.winfo_reqheight()
        positionRight = int(self.pop1.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.pop1.winfo_screenheight()/2 - popup_height/2 )
        self.pop1.geometry("+{}+{}".format(positionRight, positionDown))

        lights_config = csv_read()[config_dict['lights_config']]
        self.start1, self.dur1 = tk.IntVar(self.pop1), tk.IntVar(self.pop1)
        self.start1.set(lights_config[4])
        self.dur1.set(lights_config[8])

        tk.Label(self.pop1, text="Start").grid(row=0, column=0, padx=(100,0), pady=(20,0))
        tk.Label(self.pop1, text="Duration").grid(row=1, column=0, padx=(100,0))

        tk.Entry(self.pop1, width=9, bg="white", textvariable=self.start1).grid(row=0, column=1, pady=(20,0), padx=(0,100))
        tk.Entry(self.pop1, width=9, bg="white", textvariable=self.dur1).grid(row=1, column=1, padx=(0,100))

        tk.Button(self.pop1, text="SAVE", width=9, command=lambda: [self.save1(), self.pop1.destroy()]).grid(row=2, column=0, columnspan=2, padx=(20,20), pady=(20,20))

        self.pop1.mainloop()

    # saves shelf 1 start/duration values
    def save1(self):
        lights_config = csv_read()[config_dict['lights_config']]
        lights_config[4] = self.start1.get()
        lights_config[8] = self.dur1.get()
        csv_write('lights_config', lights_config)

    # shelf 2 popup window: for setting start and duration times
    def pop2(self):
        self.pop2 = tk.Tk()
        self.pop2.wm_title("Shelf 2")
        popup_width = self.pop2.winfo_reqwidth()
        popup_height = self.pop2.winfo_reqheight()
        positionRight = int(self.pop2.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.pop2.winfo_screenheight()/2 - popup_height/2 )
        self.pop2.geometry("+{}+{}".format(positionRight, positionDown))

        lights_config = csv_read()[config_dict['lights_config']]
        self.start2, self.dur2 = tk.IntVar(self.pop2), tk.IntVar(self.pop2)
        self.start2.set(lights_config[5])
        self.dur2.set(lights_config[9])

        tk.Label(self.pop2, text="Start").grid(row=0, column=0, padx=(100,0), pady=(20,0))
        tk.Label(self.pop2, text="Duration").grid(row=1, column=0, padx=(100,0))

        tk.Entry(self.pop2, width=9, bg="white", textvariable=self.start2).grid(row=0, column=1, pady=(20,0), padx=(0,100))
        tk.Entry(self.pop2, width=9, bg="white", textvariable=self.dur2).grid(row=1, column=1, padx=(0,100))

        tk.Button(self.pop2, text="SAVE", width=9, command=lambda: [self.save2(), self.pop2.destroy()]).grid(row=2, column=0, columnspan=2, padx=(20,20), pady=(20,20))

        self.pop2.mainloop()

    # saves shelf 2 start/duration values
    def save2(self):
        lights_config = csv_read()[config_dict['lights_config']]
        lights_config[5] = self.start2.get()
        lights_config[9] = self.dur2.get()
        csv_write('lights_config', lights_config)

    # fish tank popup window: for setting start and duration times
    def popTank(self):
        self.popTank = tk.Tk()
        self.popTank.wm_title("Fish Tank")
        popup_width = self.popTank.winfo_reqwidth()
        popup_height = self.popTank.winfo_reqheight()
        positionRight = int(self.popTank.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popTank.winfo_screenheight()/2 - popup_height/2 )
        self.popTank.geometry("+{}+{}".format(positionRight, positionDown))

        lights_config = csv_read()[config_dict['lights_config']]
        self.startTank, self.durTank = tk.IntVar(self.popTank), tk.IntVar(self.popTank)
        self.startTank.set(lights_config[6])
        self.durTank.set(lights_config[10])

        tk.Label(self.popTank, text="Start").grid(row=0, column=0, padx=(100,0), pady=(20,0))
        tk.Label(self.popTank, text="Duration").grid(row=1, column=0, padx=(100,0))

        tk.Entry(self.popTank, width=9, bg="white", textvariable=self.startTank).grid(row=0, column=1, pady=(20,0), padx=(0,100))
        tk.Entry(self.popTank, width=9, bg="white", textvariable=self.durTank).grid(row=1, column=1, padx=(0,100))

        tk.Button(self.popTank, text="SAVE", width=9, command=lambda: [self.saveTank(), self.popTank.destroy()]).grid(row=2, column=0, columnspan=2, padx=(20,20), pady=(20,20))

        self.popTank.mainloop()

    # saves fish tank start/duration values
    def saveTank(self):
        lights_config = csv_read()[config_dict['lights_config']]
        lights_config[6] = self.startTank.get()
        lights_config[10] = self.durTank.get()
        csv_write('lights_config', lights_config)

    # basking popup window: for setting start and duration times
    def popBask(self):
        self.popBask = tk.Tk()
        self.popBask.wm_title("Basking")
        popup_width = self.popBask.winfo_reqwidth()
        popup_height = self.popBask.winfo_reqheight()
        positionRight = int(self.popBask.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popBask.winfo_screenheight()/2 - popup_height/2 )
        self.popBask.geometry("+{}+{}".format(positionRight, positionDown))

        lights_config = csv_read()[config_dict['lights_config']]
        self.startBask, self.durBask = tk.IntVar(self.popBask), tk.IntVar(self.popBask)
        self.startBask.set(lights_config[7])
        self.durBask.set(lights_config[11])

        tk.Label(self.popBask, text="Start").grid(row=0, column=0, padx=(100,0), pady=(20,0))
        tk.Label(self.popBask, text="Duration").grid(row=1, column=0, padx=(100,0))

        tk.Entry(self.popBask, width=9, bg="white", textvariable=self.startBask).grid(row=0, column=1, pady=(20,0), padx=(0,100))
        tk.Entry(self.popBask, width=9, bg="white", textvariable=self.durBask).grid(row=1, column=1, padx=(0,100))

        tk.Button(self.popBask, text="SAVE", width=9, command=lambda: [self.saveBask(), self.popBask.destroy()]).grid(row=2, column=0, columnspan=2, padx=(20,20), pady=(20,20))

        self.popBask.mainloop()

    # saves basking start/duration values
    def saveBask(self):
        lights_config = csv_read()[config_dict['lights_config']]
        lights_config[7] = self.startBask.get()
        lights_config[11] = self.durBask.get()
        csv_write('lights_config', lights_config)


class WaterPump(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #title
        tk.Label(self, text="Water Pump", bg="white", font=TITLE_FONT).pack(pady = 10)
        #navigation button
        navibutton1 = tk.Button(self, text="Back", width=9, command=lambda: controller.show_frame(ControlPanel))
        navibutton1.pack(pady = (0,10))
        
        # initialize tkinter variables for rate and time values
        self.rateA, self.rateB, self.time = tk.IntVar(), tk.IntVar(), tk.IntVar()
        pump_config = csv_read()[config_dict['pump_config']]
        self.rateA.set(pump_config[0])
        self.rateB.set(pump_config[1])
        self.time.set(pump_config[2])
        self.mode = pump_config[3]

        # initialize param text and padding text
        self.buttonFrame = tk.Frame(master=self, bg='white')
        self.buttonFrame.pack()
        tk.Label(master=self.buttonFrame, text="aaaaaaaaaaaaa", bg="white", fg="white").grid(row=1, column=0)
        tk.Label(master=self.buttonFrame, text="aaaaaaaaaaaaa", bg="white", fg="white").grid(row=1, column=3, columnspan=2)
        tk.Label(master=self.buttonFrame, text="Flow Control:", bg="white").grid(row=0, column=1, sticky="E")
        tk.Label(master=self.buttonFrame, text="Bed A Flow Rate (gal/hr):", bg="white").grid(row=1, column=1)
        tk.Label(master=self.buttonFrame, text="Bed B Flow Rate (gal/hr):", bg="white").grid(row=2, column=1)

        # initialize entry boxes and buttons
        self.control = tk.Button(master=self.buttonFrame, text="OFF", fg="red", width=9, command=self.switch)
        self.control.grid(row=0, column=2, padx=5, pady=8)
        tk.Entry(master=self.buttonFrame, width=9, textvariable=self.rateA, bg="white").grid(row=1, column=2, padx=5, pady=5)
        tk.Entry(master=self.buttonFrame, width=9, textvariable=self.rateB, bg="white").grid(row=2, column=2, padx=5, pady=5)
        
        tk.Button(self, text="Save", width=9, command=self.popup).pack(pady = (10,0))

        # initialize correct button state
        if self.mode == "off":
            self.mode = "go to off"
        elif self.mode == "on":
            self.mode = "off"
        else:
            self.mode = "on"
        self.switch()

    # switches the button state betwee 'off'/'on'/'timer'
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
        config_settings = csv_read()
        pump_config = [config_settings[config_dict['pump_config']][0], config_settings[config_dict['pump_config']][1], \
            config_settings[config_dict['pump_config']][2], self.mode]
        csv_write('pump_config', pump_config)

    # save popup
    def popup(self):
        self.popup = tk.Tk()
        self.popup.wm_title("Alert")
        label = ttk.Label(self.popup, text="Are you sure you want to save?", font=MEDIUM_FONT)
        label.grid(row=0, columnspan=14, pady=(10,20), padx = (100,100))
        
        # centers the popup window
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()
        positionRight = int(self.popup.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popup.winfo_screenheight()/2 - popup_height/2 )
        self.popup.geometry("+{}+{}".format(positionRight, positionDown))
        
        YesB = ttk.Button(self.popup, text="YES", command = lambda:[self.save(), self.popup.destroy()])
        YesB.grid(row=1, column=1, padx =(100,10), pady = (0,10))
        NoB = ttk.Button(self.popup, text="NO", command = self.popup.destroy)
        NoB.grid(row=1, column=2, padx=(10,100), pady = (0,10))
        self.popup.mainloop()
    
    # saves data to the csv
    def save(self):
        if self.mode == "timer":
            real_time = self.timer.get()
        else:
            real_time = None
        pump_config = [self.rateA.get(), self.rateB.get(), real_time, self.mode]
        csv_write('pump_config', pump_config)
        

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
        navibutton1 = ttk.Button(self, text="Back", command=lambda: controller.show_frame(ControlPanel))
        navibutton1.pack(pady = (0,10))
        
        self.buttonFrame = tk.Frame(master=self, bg='white')
        self.buttonFrame.pack()
        
        # init labels
        tk.Label(master=self.buttonFrame, text="pH", bg="white").grid(row=0, column=0)
        tk.Label(master=self.buttonFrame, text="TDS", bg="white").grid(row=1, column=0)
        tk.Label(master=self.buttonFrame, text="Nitrate", bg="white").grid(row=2, column=0)
        tk.Label(master=self.buttonFrame, text="Ammonia", bg="white").grid(row=3, column=0)

        # init on/off buttons
        self.phTog = tk.Button(master=self.buttonFrame, text="OFF", fg="red", width=9, command=lambda: self.switch(0))
        self.tdsTog = tk.Button(master=self.buttonFrame, text="OFF", fg="red", width=9, command=lambda: self.switch(1))
        self.nitTog = tk.Button(master=self.buttonFrame, text="OFF", fg="red", width=9, command=lambda: self.switch(2))
        self.amTog = tk.Button(master=self.buttonFrame, text="OFF", fg="red", width=9, command=lambda: self.switch(3))
        self.phTog.grid(row=0, column=1, padx=5, pady=8)
        self.tdsTog.grid(row=1, column=1, padx=5, pady=8)
        self.nitTog.grid(row=2, column=1, padx=5, pady=8)
        self.amTog.grid(row=3, column=1, padx=5, pady=8)

        # init calibrate buttons
        tk.Button(master=self.buttonFrame, text="Calibrate", width=9, command=self.popPh).grid(row=0, column=2, padx=5, pady=8)
        tk.Button(master=self.buttonFrame, text="Calibrate", width=9, command=self.popTds).grid(row=1, column=2, padx=5, pady=8)
        tk.Button(master=self.buttonFrame, text="Calibrate", width=9, command=self.popNit).grid(row=2, column=2, padx=5, pady=8)
        tk.Button(master=self.buttonFrame, text="Calibrate", width=9, command=self.popAm).grid(row=3, column=2, padx=5, pady=8)

        # init on/off values
        for i in range(4):
            sensor_config = csv_read()[config_dict['sensor_config']]
            if sensor_config[i] == "on":
                sensor_config[i] = "off"
                csv_write('sensor_config', sensor_config)
                self.switch(i)

    # given param index, switches it between 'on'/'off'
    def switch(self, i):
        sensor_config = csv_read()[config_dict['sensor_config']]
        if sensor_config[i] == "off":
            sensor_config[i] = "on"
            if i == 0:
                self.phTog.config(text="ON", fg="green")
            elif i == 1:
                self.tdsTog.config(text="ON", fg="green")
            elif i == 2:
                self.nitTog.config(text="ON", fg="green")
            elif i == 3:
                self.amTog.config(text="ON", fg="green")
        else:
            sensor_config[i] = "off"
            if i == 0:
                self.phTog.config(text="OFF", fg="red")
            elif i == 1:
                self.tdsTog.config(text="OFF", fg="red")
            elif i == 2:
                self.nitTog.config(text="OFF", fg="red")
            elif i == 3:
                self.amTog.config(text="OFF", fg="red")
        csv_write('sensor_config', sensor_config)
    
    # ph popup window: for sample calibration values
    def popPh(self):
        self.popPh = tk.Tk()
        self.popPh.wm_title("Calibrate pH")
        popup_width = self.popPh.winfo_reqwidth()
        popup_height = self.popPh.winfo_reqheight()
        positionRight = int(self.popPh.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popPh.winfo_screenheight()/2 - popup_height/2 )
        self.popPh.geometry("+{}+{}".format(positionRight, positionDown))

        tk.Label(self.popPh, text="Sample").grid(row=1, column=0, padx=(100,0), pady=(20,0))
        tk.Label(self.popPh, text="Sample").grid(row=2, column=0, padx=(100,0))
        tk.Label(self.popPh, text="Sample").grid(row=3, column=0, padx=(100,0))
        tk.Label(self.popPh, text="Sample").grid(row=4, column=0, padx=(100,0), pady=(0,20))

        tk.Entry(self.popPh, width=9, bg="white").grid(row=1, column=1, pady=(20,0))
        tk.Entry(self.popPh, width=9, bg="white").grid(row=2, column=1)
        tk.Entry(self.popPh, width=9, bg="white").grid(row=3, column=1)
        tk.Entry(self.popPh, width=9, bg="white").grid(row=4, column=1, pady=(0,20))

        tk.Button(self.popPh, text="SET", width=9).grid(row=2, column=3, padx=(20,100))
        tk.Button(self.popPh, text="CLEAR", width=9).grid(row=3, column=3, padx=(20,100))

        self.popPh.mainloop()

    # tds popup window: for sample calibration values
    def popTds(self):
        self.popTds = tk.Tk()
        self.popTds.wm_title("Calibrate TDS")
        popup_width = self.popTds.winfo_reqwidth()
        popup_height = self.popTds.winfo_reqheight()
        positionRight = int(self.popTds.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popTds.winfo_screenheight()/2 - popup_height/2 )
        self.popTds.geometry("+{}+{}".format(positionRight, positionDown))

        tk.Label(self.popTds, text="Sample").grid(row=1, column=0, padx=(100,0), pady=(20,0))
        tk.Label(self.popTds, text="Sample").grid(row=2, column=0, padx=(100,0))
        tk.Label(self.popTds, text="Sample").grid(row=3, column=0, padx=(100,0))
        tk.Label(self.popTds, text="Sample").grid(row=4, column=0, padx=(100,0), pady=(0,20))

        tk.Entry(self.popTds, width=9, bg="white").grid(row=1, column=1, pady=(20,0))
        tk.Entry(self.popTds, width=9, bg="white").grid(row=2, column=1)
        tk.Entry(self.popTds, width=9, bg="white").grid(row=3, column=1)
        tk.Entry(self.popTds, width=9, bg="white").grid(row=4, column=1, pady=(0,20))

        tk.Button(self.popTds, text="SET", width=9).grid(row=2, column=3, padx=(20,100))
        tk.Button(self.popTds, text="CLEAR", width=9).grid(row=3, column=3, padx=(20,100))

        self.popTds.mainloop()
    
    # nitrogen popup window: for sample calibration values
    def popNit(self):
        self.popNit = tk.Tk()
        self.popNit.wm_title("Calibrate Nitrate")
        popup_width = self.popNit.winfo_reqwidth()
        popup_height = self.popNit.winfo_reqheight()
        positionRight = int(self.popNit.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popNit.winfo_screenheight()/2 - popup_height/2 )
        self.popNit.geometry("+{}+{}".format(positionRight, positionDown))

        tk.Label(self.popNit, text="Sample").grid(row=1, column=0, padx=(100,0), pady=(20,0))
        tk.Label(self.popNit, text="Sample").grid(row=2, column=0, padx=(100,0))
        tk.Label(self.popNit, text="Sample").grid(row=3, column=0, padx=(100,0))
        tk.Label(self.popNit, text="Sample").grid(row=4, column=0, padx=(100,0), pady=(0,20))

        tk.Entry(self.popNit, width=9, bg="white").grid(row=1, column=1, pady=(20,0))
        tk.Entry(self.popNit, width=9, bg="white").grid(row=2, column=1)
        tk.Entry(self.popNit, width=9, bg="white").grid(row=3, column=1)
        tk.Entry(self.popNit, width=9, bg="white").grid(row=4, column=1, pady=(0,20))

        tk.Button(self.popNit, text="SET", width=9).grid(row=2, column=3, padx=(20,100))
        tk.Button(self.popNit, text="CLEAR", width=9).grid(row=3, column=3, padx=(20,100))

        self.popNit.mainloop()
    
    # ammonia popup window: for sample calibration values
    def popAm(self):
        self.popAm = tk.Tk()
        self.popAm.wm_title("Calibrate Ammonia")
        popup_width = self.popAm.winfo_reqwidth()
        popup_height = self.popAm.winfo_reqheight()
        positionRight = int(self.popAm.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popAm.winfo_screenheight()/2 - popup_height/2 )
        self.popAm.geometry("+{}+{}".format(positionRight, positionDown))

        tk.Label(self.popAm, text="Sample").grid(row=1, column=0, padx=(100,0), pady=(20,0))
        tk.Label(self.popAm, text="Sample").grid(row=2, column=0, padx=(100,0))
        tk.Label(self.popAm, text="Sample").grid(row=3, column=0, padx=(100,0))
        tk.Label(self.popAm, text="Sample").grid(row=4, column=0, padx=(100,0), pady=(0,20))

        tk.Entry(self.popAm, width=9, bg="white").grid(row=1, column=1, pady=(20,0))
        tk.Entry(self.popAm, width=9, bg="white").grid(row=2, column=1)
        tk.Entry(self.popAm, width=9, bg="white").grid(row=3, column=1)
        tk.Entry(self.popAm, width=9, bg="white").grid(row=4, column=1, pady=(0,20))

        tk.Button(self.popAm, text="SET", width=9).grid(row=2, column=3, padx=(20,100))
        tk.Button(self.popAm, text="CLEAR", width=9).grid(row=3, column=3, padx=(20,100))

        self.popAm.mainloop()

class Oxygenator(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #title
        tk.Label(self, text="Oxygenator", bg="white", font=TITLE_FONT).pack(pady = 10)
        #navigation button
        navibutton1 = ttk.Button(self, text="Back", command=lambda: controller.show_frame(ControlPanel))
        navibutton1.pack(pady = (0,10))

        # init tkinter var
        self.min = tk.IntVar()
        oxygen_config = csv_read()[config_dict['oxygen_config']]
        self.min.set(oxygen_config[0])
        
        # init frame
        self.buttonFrame = tk.Frame(master=self, bg='white')
        self.buttonFrame.pack()
        tk.Label(master=self.buttonFrame, text="Current DO (ppm):", bg="white").grid(row=0, column=0)
        tk.Entry(master=self.buttonFrame, width=9, textvariable=self.min, bg="white").grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self, text="Save", width=9, command=self.popup).pack(pady = (10,0))

    # save popup
    def popup(self):
        self.popup = tk.Tk()
        self.popup.wm_title("Alert")
        label = ttk.Label(self.popup, text="Are you sure you want to save?", font=MEDIUM_FONT)
        label.grid(row=0, columnspan=14, pady=(10,20), padx = (100,100))
        
        # centers the popup window
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()
        positionRight = int(self.popup.winfo_screenwidth()/2 - popup_width/2 )
        positionDown = int(self.popup.winfo_screenheight()/2 - popup_height/2 )
        self.popup.geometry("+{}+{}".format(positionRight, positionDown))
        
        YesB = ttk.Button(self.popup, text="YES", command = lambda:[self.save(), self.popup.destroy()])
        YesB.grid(row=1, column=1, padx =(100,10), pady = (0,10))
        NoB = ttk.Button(self.popup, text="NO", command = self.popup.destroy)
        NoB.grid(row=1, column=2, padx=(10,100), pady = (0,10))
        self.popup.mainloop()
    
    # saves value to csv
    def save(self):
        csv_write('oxygen_config', [self.min.get()])

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
#app.geometry('1280x623')
app.geometry('1917x970')
#this makes app full screen, not sure if it's good for us or not
#app.attributes('-fullscreen', True)
#update animation first
ani = animation.FuncAnimation(f, animate, interval=5000)
#mainloop
app.mainloop()
