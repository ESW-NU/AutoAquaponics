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
#import libraries for distance sensor
    import time
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM) #GPIO Mode (BOARD / BCM)
#create ADS object
    ads = ADS.ADS1115(i2c)
    ads.gain = 2/3
#single ended mode read for pin 0 and 1
    chan = AnalogIn(ads, ADS.P0)
    chan1 = AnalogIn(ads, ADS.P1)
#define readings from ADC
    pH = -5.82*chan.voltage + 22.1 #calibrated equation
    #pH = chan.voltage
    TDS = chan1.voltage
#read air temp and air humidity
    hum, atemp = dht.read_retry(dht.DHT22, DHT)
#read w1 water temp sensor
    wtemp = wt_sensor.get_temperature()
#setup distance sensing stuff
    GPIO_TRIGGER = 6 #set GPIO Pins
    GPIO_ECHO = 18
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT) #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    
    return pH, TDS, hum, atemp, wtemp, distance

#from time import sleep
#while True:
#    print(getData())
#    sleep(0.2)