#from bluepy import btle

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
            str(self.charact[char]) + ", " + bin(message) + ", " + str(message))

    # peri is the code for the specific peripheral we are disconnecting
    def BLE_disconnect(self, peri):
        print(self.peripheral[peri])

