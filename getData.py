def getData():
#import necessary modules and initialize I2C bus
    import board
    import busio
    i2c = busio.I2C(board.SCL, board.SDA)
#import board module (ADS1115)
    import adafruit_ads1x15.ads1115 as ADS
#import ADS1x15 library's version of AnalogIn
    from adafruit_ads1x15.analog_in import AnalogIn
#import Adafruit DHT22 stuff (humidty)
    import Adafruit_DHT as dht
    DHT = 14 #set DHT's GPIO pin number
#import the w1 water temp sensor module
    from w1thermsensor import W1ThermSensor
    wt_sensor = W1ThermSensor()
#create ADS object
    ads = ADS.ADS1115(i2c)
    ads.gain = 2/3
#single ended mode read for pins 0 and 1
    chan = AnalogIn(ads, ADS.P0)
    chan1 = AnalogIn(ads, ADS.P1)
#read air temp and air humidity
    hum, atemp = dht.read_retry(dht.DHT22, DHT)
#read w1 water temp sensor
    wtemp = wt_sensor.get_temperature()
    return tuple(chan.voltage, hum, atemp, wtemp) #chan.voltage == ph

#from time import sleep
#while True:
#    print(getData())
#    sleep(2)