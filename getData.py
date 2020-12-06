def getData(temp_distance):
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
#read w1 water temp sensor
    wtemp = wt_sensor.get_temperature()
#create ADS object
    ads = ADS.ADS1115(i2c)
    ads.gain = 2/3
#single ended mode read for pin 0 and 1
    chan = AnalogIn(ads, ADS.P0)
    chan1 = AnalogIn(ads, ADS.P1)
#define readings from ADC
    pH = -5.82*chan.voltage + 22.1 #calibrated equation
    #pH = chan.voltage
    '''calibrate TDS here'''
    Vtds_raw = chan1.voltage #raw reading from sensor right now
    TheoEC = 684 #theoretical EC of calibration fluid
    Vc = 1.085751885 #v reading of sensor when calibrating
    temp_calibrate = 23.25 #measured water temp when calibrating
    rawECsol = TheoEC*(1+0.02*(temp_calibrate-25)) #temp compensate the calibrated values
    K = (rawECsol)/(133.42*(Vc**3)-255.86*(Vc**2)+857.39*Vc)#defined calibration factor K
    EC_raw = K*(133.42*(Vtds_raw**3)-255.86*(Vtds_raw**2)+857.39*Vtds_raw)
    EC = EC_raw/(1+0.02*(wtemp-25)) #use current temp for temp compensation
    TDS = EC/2 #TDS is just half of electrical conductivity in ppm
#read air temp and air humidity
    hum, atemp = dht.read_retry(dht.DHT22, DHT)
#setup distance sensing stuff
    new_reading = False
    counter = 0
    GPIO_TRIGGER = 6 #set GPIO Pins
    GPIO_ECHO = 18
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT) #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
    # set Trigger to HIGH
    StopTime = time.time()
    GPIO.output(GPIO_TRIGGER, True)
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00006)
    GPIO.output(GPIO_TRIGGER, False)
    StartTime = time.time()
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        pass
        counter += 1 #stop loop if it gets stuck
        if counter == 5000:
            new_reading = True
            break
    StartTime = time.time()
    
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        pass
    StopTime = time.time()
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    if new_reading:
        distance = temp_distance
    else:
        distance = (TimeElapsed * 34300)/2
    #make sure distance is the last value on this list
    return pH, TDS, hum, atemp, wtemp, distance

#from time import sleep
#from datetime import datetime
#while True:
#     print('updating...')
#     print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"),getData())
#     sleep(5)