from bluepy import btle
import datetime

class ParentBLE:
    def __init__(self):
        raise NotImplementedError
    
    def BLE_write(self, char, message):
        raise NotImplementedError
    
    def BLE_disconnect(self, peri):
        raise NotImplementedError
    
    
    def brown(self, n):
        return n << 21 # bits 21-31
    
    def red(self, n):
        return n << 10 # bits 10-20

    def blue(self, n):
        return n << 2 # bits 2-9

    # yellow is bits 0-1

    
    def BLE_init(self):
        # initialization start
        now = datetime.datetime.now()
        time = [int(x) for x in now.strftime("%H:%M").split(":")]
        time = 6 * time[0] + time[1]//10
        red = self.red(time) # current time
        blue = 0 # stop timer
        yellow = 0 # init identifier
        message = red | blue | yellow
        self.BLE_write('0', message)
        
        # initialization end
        blue = self.blue(1) # restart timer
        yellow = 0 # init identifier
        message = blue | yellow
        self.BLE_write('0', message)

    def BLE_pump_mode(self, mode):
        blue = self.blue(0) # water pump outlet 0 (will be 2 pumps)
        yellow = 3
        if mode == 'on':
            brown = self.brown(1)
            red = self.red(1)
        elif mode == 'off':
            brown = 0
            red = self.red(1)
        else:
            brown = 0
            red = 0
        message = brown | red | blue | yellow
        self.BLE_write('0', message)

    def BLE_solenoid_interval(self, bed, timer):
        red = self.red(timer)
        outlet = 15 if bed == 'bed-A' else 16  # solenoid A = outlet 15, solenoid B = outlet 16
        blue = self.blue(outlet)
        yellow = 1
        message = red | blue | yellow
        self.BLE_write('0', message)

    def BLE_lights_mode(self, index, mode):
        if mode == 'on':
            brown = self.brown(1)
            red = self.red(1)
        elif mode == 'off':
            brown = 0
            red = self.red(1)
        else:
            brown = 0
            red = 0
        blue = self.blue(index+1) # outlets: shelf1=1, shelf2=2, fish=3, basking=4
        yellow = 3
        message = brown | red | blue | yellow
        self.BLE_write('0', message)

    def BLE_lights_duration(self, index, starthh, startmm, durationhh, durationmm, am_pm):
        if am_pm == 'AM' and starthh == 12:
            starthh = 0
        elif am_pm == 'PM' and starthh < 12:
            starthh += 12
        start = 60 * starthh + startmm
        duration = 60 * durationhh + durationmm
        brown = self.brown(duration)
        red = self.red(start)
        blue = self.blue(index)
        yellow = 2
        message = brown | red | blue | yellow
        self.BLE_write('0', message)


class BLE(ParentBLE):
    def __init__(self):
        print("Connecting to BLE...")
        #Device 1 (outlet box)
        self.p = btle.Peripheral("AC:67:B2:35:4D:2E") #unique address of our ESP32 in office
        self.s = self.p.getServiceByUUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b")
        self.c = self.s.getCharacteristics()[0]
        print("Connected!")
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
        self.charact[char].write(message.to_bytes(4, byteorder='big'))
        print("BLE message here: ", str(self.charact[char]), ", " + bin(message), ", ", message)

    # peri is the code for the specific peripheral we are disconnecting
    def BLE_disconnect(self, peri):
        print(self.peripheral[peri])
    

class FakeBLE(ParentBLE):
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
        print("Fake message here: ", str(self.charact[char]), ", " + bin(message), ", ", message)

    # peri is the code for the specific peripheral we are disconnecting
    def BLE_disconnect(self, peri):
        print(self.peripheral[peri])