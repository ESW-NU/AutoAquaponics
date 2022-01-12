#from bluepy import btle
import datetime
from tkinter import Message

class BLE:
    def __init__(self):
        print("Connecting to BLE...")
        #Device 1 (outlet box)
        self.p = btle.Peripheral("AC:67:B2:37:2A:22") #unique address of our ESP32 in office
        self.s = self.p.getServiceByUUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b")
        self.c = self.s.getCharacteristics()[0]

        # Device 2 (name of device)
        # self.p1 = btle.Peripheral("insert id here") #follow this format, so on and so forth
        # self.s1 = self.p1.getServiceByUUID("enter id here")
        # self.c1 = self.s1.getCharacteristics()[0]

        self.charact = { #we are using dictionaries to map input keys to specific characteristics/peripherals defined above
            "0": self.c, #outlet box, characteristic code is 0, char is c
            "1": self.c, #change to a different characteristic later on
            "2": self.c,
            "3": self.c
            #'4':c1 #another chara
        }

        self.peripheral = {
            "0": self.p, #the actual outlet box peripheral
            "1": self.p, #change to a different peripheral later on, p1 or something
            "2": self.p,
            "3": self.p
            #'4':p1 #another peripheral
        }

    # char is the characteristic we are writing to, message is the number we are sending
    def BLE_write(self, char, message):
        self.charact[char].write(bytes([message]))

    # peri is the code for the specific peripheral we are disconnecting
    def BLE_disconnect(self, peri):
        self.peripheral[peri].disconnect()

class fakeBLE:
    def __init__(self):
        print("Connecting to fake BLE...")
        self.c = "Outlet Box Characteristic"
        self.p = "Outlet Box Peripheral"
        self.charact = { #we are using dictionaries to map input keys to specific characteristics/peripherals defined above
            "0": self.c, #outlet box, characteristic code is 0, char is c
            "1": self.c, #change to a different characteristic later on
            "2": self.c,
            "3": self.c
            #'4':c1 #another chara
        }

        self.peripheral = {
            "0": self.p, #the actual outlet box peripheral
            "1": self.p, #change to a different peripheral later on, p1 or something
            "2": self.p,
            "3": self.p
            #'4':p1 #another peripheral
        }

    # char is the characteristic we are writing to, message is the number we are sending
    def BLE_write(self, char, message):
        print("Fake message here: " + 
            str(self.charact[char]) + ", " + format(message,"032b") + ", " + str(message))

    # peri is the code for the specific peripheral we are disconnecting
    def BLE_disconnect(self, peri):
        print(self.peripheral[peri])
    
    # this pulls CSV data from config.csv and generates a list of messages using BLE_message
    def BLE_read(self):
        from main import user_settings
        import csv
        config_path, db_path, img_path = user_settings()
        with open(config_path, "r") as file:
            config = list(csv.reader(file))

    def BLE_messenger(self,mode,outlet):
        brown = "0000000000" # 10 bit
        red = "0000000000" # 10 bit
        blue = "0000000000" # 10 bit
        yellow = "00" # 2 bit 
        # send start message
        # self.start_msg()
        # message: permanent turn on(1) or off(0)
        if mode == 1 or mode == 0:
            yellow = "11" # indicate permanant mode
            brown = "000000000" + str(mode)
            red = "0000000001"
            blue = format(outlet-1,"010b")
        # message: timer toggle button
        elif mode == 2:
            yellow = "11"
        # message: timer save button
        elif mode == 3:
            yellow = "10"

        message = brown+red+blue+yellow
        #message = format(int(message,2),"032b")
        message = int(message,2)
        return message

    def start_msg(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M").split(":")
        current_time = round(int(current_time[0])*6 + int(current_time[1])/10) 
        # print(str(current_time))
        

    # this generates the individual 32 bit binary messages we are sending
    def BLE_message(self, mode, type, index_pump_outlets, time, state, interval=0b0):
        if mode == 0b00: #remove alarm mode
            if type == 0b0000 or 0b1100: #start message or end message
                message = type | mode
            if type == 0b0100: #indexing pump mode
                message = index_pump_outlets | interval | type | mode
        if mode == 0b01 or 0b10: #add weekly or daily alarm mode
            current_time = datetime.datetime.now().strftime("%w/%H/%M").split("/") #makes list ["day of week in int", "hour in 24 hr int", "min in int"]
            current_time = round(int(current_time[0])*144 + int(current_time[1])*6 + int(current_time[2])/10) << 22
            #toggle time will always start on Monday if it's daily mode (0b10)
            toggle_time = time.strftime("%w/%H/%M").split("/") #makes list ["day of week in int", "hour in 24 hr int", "min in int"]
            toggle_time = round(int(toggle_time[0])*144 + int(toggle_time[1])*6 + int(toggle_time[2])/10) << 12
            message = current_time | toggle_time | state | mode
        
        if mode == 0b11: #set permanent state mode
            current_time = 0b0
            message = state | type

        print(message)
        return message
