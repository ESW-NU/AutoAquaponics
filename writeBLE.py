from bluepy import btle
from time import sleep
 
print("Connecting...")
p = btle.Peripheral("AC:67:B2:37:2A:22") #unique address of our ESP32 in office

print("Services...")
for svc in p.services:
    print(str(svc))

    
s = p.getServiceByUUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b")
c = s.getCharacteristics()[0]

#c.write(bytes("5", "utf-8")) #change the number to change frequency, what is utf-8 in hex?
print("write fast")
c.write(bytes([50]))
sleep(1)
print("write slow")
c.write(bytes([200]))
sleep(2)
print("done")