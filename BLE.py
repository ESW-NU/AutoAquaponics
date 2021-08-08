from bluepy import btle
from time import sleep

class BLE:
    def __init__(self):
        print("Connecting...")
    #Device 1 (outlet box)
        self.p = btle.Peripheral("AC:67:B2:37:2A:22") #unique address of our ESP32 in office
        self.s = self.p.getServiceByUUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b")
        self.c = self.s.getCharacteristics()[0]

    # Device 2 (name of device)
    # p1 = btle.Peripheral("insert id here") #follow this format, so on and so forth
    # s1 = p1.getServiceByUUID("enter id here")
    # c1 = s1.getCharacteristics()[0]

        self.charact = {
            "0": self.c, #outlet box, characteristic code is 1, char is c
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

        # print("Services...")
        # for svc in p.services:
        #     print(str(svc))
        
            
        

        #c.write(bytes("5", "utf-8")) #change the number to change frequency, what is utf-8 in hex?
        # print("write fast")
        # c.write(bytes([50]))
        # sleep(1)
        # print("write slow")
        # c.write(bytes([200]))
        # sleep(2)
        # print("done")

    def BLE_disconnect(peri):
        self.peripheral[peri].disconnect()
