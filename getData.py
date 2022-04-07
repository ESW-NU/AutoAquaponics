#initialize GPIO pins for TDS sensor switch + distance sensor
pin_num = 17
pin_num2 = 27
import time, sys
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pin_num,GPIO.OUT)
GPIO.setup(pin_num2,GPIO.OUT)
import sys
import time #need this for sleep and distance sensor
from time import sleep
#import necessary modules and initialize I2C bus
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
#import board module (ADS1115)
import adafruit_ads1x15.ads1115 as ADS
#import ADS1x15 library's version of AnalogIn
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_dht
dhtDevice = adafruit_dht.DHT22(board.D14, use_pulseio=False)
#import the w1 water temp sensor module
import glob
import time

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#create ADS object
ads = ADS.ADS1115(i2c)
ads.gain = 2/3
#single ended mode read for pin 0 and 1
chan = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
#import numpy for NaN
import numpy as np

def getData(last_distance, last_wtemp, last_hum, last_atemp): #main function that calls on all other functions to generate data list
#read w1 water temp sensor
    wtemp = getWTemp()
    GPIO.output(pin_num,GPIO.HIGH) #turn TDS sensor on
    #GPIO.output(pin_num2,GPIO.HIGH)
    sleep(0.5)
    #call TDS function to get a value while pin is HIGH
    if wtemp == np.nan: #use last wtemp value if it's NaN
        TDS = getTDS(last_wtemp)
    else:
        TDS = getTDS(wtemp)        
    GPIO.output(pin_num,GPIO.LOW) #turn TDS sensor off
    #GPIO.output(pin_num2,GPIO.LOW)
    sleep(0.5)
#define readings from ADC
    pH = -5.82*chan.voltage + 22.1 #calibrated equation
    #pH = chan.voltage
#read air temp and air humidity
    atemp, hum = getDHT()#dht.read_retry(dht.DHT22, DHT)
    if hum == np.nan or atemp == np.nan:
        hum, atemp = last_hum, last_atemp
    distance = getDistance(last_distance)
    
#read flow rate
    #flow1 = getFlowRate(12, 4.8)
    #flow2 = getFlowRate(13, 0.273)
    #make sure distance is the last value on this list
    #order should be pH, TDS, hum, atemp, wtemp, distance
    return pH, TDS, hum, atemp, wtemp, distance#, flow1, flow2

#DS18B20 functions
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def getWTemp():
    lines = read_temp_raw()
    #print(lines)
    if len(lines) > 0: #only index below if lines is not empty
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            #print("temp_c = " + str(temp_c))
            return temp_c
    else:
        print("READING DS18B20 AGAIN!")
        return getWTemp() #rerun function again
        
#TDS sensor function
def getTDS(wtemp):
    Vtds_raw = chan1.voltage #raw reading from sensor right now
    TheoEC = 684 #theoretical EC of calibration fluid
    Vc = 1.085751885 #v reading of sensor when calibrating
    temp_calibrate = 23.25 #measured water temp when calibrating
    rawECsol = TheoEC*(1+0.02*(temp_calibrate-25)) #temp compensate the calibrated values
    K = (rawECsol)/(133.42*(Vc**3)-255.86*(Vc**2)+857.39*Vc)#defined calibration factor K
    EC_raw = K*(133.42*(Vtds_raw**3)-255.86*(Vtds_raw**2)+857.39*Vtds_raw)
    EC = EC_raw/(1+0.02*(wtemp-25)) #use current temp for temp compensation
    TDS = EC/2 #TDS is just half of electrical conductivity in ppm
    return TDS

#DHT function
def getDHT():
    temperature_c = np.nan
    humidity = np.nan
    while is_nan(temperature_c) or is_nan(humidity):#test to see if the value is still nan
        #print('Running DHT...') #can comment out later, just here to test reliability
        try:
            # get temp and humidity
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            temperature_c = float('NaN')
            humidity = float('NaN')
            #continue
        except Exception as error:
            dhtDevice.exit()
            raise error
    return temperature_c, humidity

def is_nan(x): #used in DHT function
    return (x is np.nan or x != x)

def getDistance(last_distance): #output distance in cm
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
        return last_distance
    else:
        return (TimeElapsed * 34300)/2

def getFlowRate(FLOW_SENSOR_GPIO, k):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FLOW_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    global count
    count = 0
    start_counter = 0
    def countPulse(channel):
       global count
       if start_counter == 1:
          count = count+1
    
    GPIO.add_event_detect(FLOW_SENSOR_GPIO, GPIO.FALLING, callback=countPulse)

    
    try:
        start_counter = 1
        time.sleep(1)
        start_counter = 0
        flow = (count / k)*15.850323141489 # Pulse frequency (Hz) = 0.2Q, Q is flow rate in GPH.
        print("The flow is: %.3f GPH" % (flow))
        print("The count is: " + str(count))
        count = 0
        time.sleep(0.1)
    except KeyboardInterrupt:
        print('\nkeyboard interrupt!')
        GPIO.cleanup()
        sys.exit()
'''
from time import sleep
from datetime import datetime
while True:
     print('updating...')
     print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"),getData(1, 1, 1, 1))
     sleep(1)
    '''