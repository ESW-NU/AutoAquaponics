from bluepy import btle
 
print("Connecting...")
p = btle.Peripheral("AC:67:B2:36:AF:A2") #unique address of our ESP32 in office

print("Services...")
for svc in p.services:
    print(str(svc))

    
s = p.getServiceByUUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b")
c = s.getCharacteristics()[0]

c.write(bytes("5", "utf-8")) #change the number to change frequency, what is utf-8 in hex?
print("done")
p.disconnect()

'''
Two issues with this code:
    1. After running this once, the ESP32 disappears from the BLE scanner and can no longer be written to again by the Pi unless it's rebooted. This behavior doesn't happen
    with the iPhone BLEScanner app so it must be something on the Pi's side
    2. Line 14 above withe c.write doesn't actually write the correct number in there, it turns whatever is
    in the "" into ascii and then to hex (e.g. if we do "0" it actually writes 0x30 to the ESP32)

These two problems need to be fixed
'''