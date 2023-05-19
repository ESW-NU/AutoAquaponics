import time
import RPi.GPIO as GPIO
import math

#Waveshare ADC Hat Initialization
#######################
REF = 5           # Modify according to actual voltage
                    # external AVDD and AVSS(Default), or internal 2.5V
# ADC1 test part
TEST_ADC1       = True
# ADC2 test part
TEST_ADC2       = False
# ADC1 rate test part, For faster speeds use the C program
TEST_ADC1_RATE   = False
# RTD test part 
TEST_RTD        = False
#######################

#initialize GPIO pins for TDS sensor switch + distance sensor
pin_num = 17
pin_num2 = 27
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pin_num,GPIO.OUT)
GPIO.setup(pin_num2,GPIO.OUT)
import time #need this for sleep and distance sensor
from time import sleep

import serial #for TEROS sensor to interface with Arduino

#initalize debugging LED
GPIO.setup(25, GPIO.OUT)

from VL53L0x_rasp_python.python import VL53L0X
# Create a VL53L0X object
tof = VL53L0X.VL53L0X(i2c_bus=1,i2c_address=0x29)
#import necessary modules and initialize I2C bus
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
#import board module (ADS1115)
import adafruit_ads1x15.ads1115 as ADS
#import ADS1x15 library's version of AnalogIn
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_extended_bus import ExtendedI2C as I2C
i2c4 = I2C(4)
#import Adafruit DHT22 stuff (humidty)
#import Adafruit_DHT as dht
#import adafruit_dht
#DHT = 14 #set DHT's GPIO pin number
#dhtDevice = adafruit_dht.DHT22(board.D14, use_pulseio=False)
#import the w1 water temp sensor module
#from w1thermsensor import W1ThermSensor
#wt_sensor = W1ThermSensor()
import glob
import time

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#read serial for Arduino
try:
    ser = serial.Serial('/dev/ttyACM0', 1200, timeout=1)
except:
    print("/dev/ttyACM0 not found, trying /dev/ttyACM1")
    ser = serial.Serial('/dev/ttyACM1', 1200, timeout=1)

# UNCOMMENT TO ADD MORE CHANNELS
adc0 = ADS.ADS1115(i2c4, address=0x48)
adc0.gain = 1
adc1 = ADS.ADS1115(i2c4, address=0x49)
adc1.gain = 1
adc2 = ADS.ADS1115(i2c4, address=0x4A)
adc2.gain = 1
adc3 = ADS.ADS1115(i2c4, address=0x4B)
adc3.gain = 1
# #create ADS objects (four different adafruit adc)
ads0 = ADS.ADS1115(i2c, address=0x48)
ads0.gain = 1
ads1 = ADS.ADS1115(i2c, address=0x49)
ads1.gain = 1
ads2 = ADS.ADS1115(i2c, address=0x4A)
ads2.gain = 1
ads3 = ADS.ADS1115(i2c, address=0x4B)
ads3.gain = 1
#differential connection read for pin 0 vs 1 and 2 vs 3
chan0 = AnalogIn(ads0, ADS.P0, ADS.P1)
chan1 = AnalogIn(ads0, ADS.P2, ADS.P3)
chan2 = AnalogIn(ads1, ADS.P0, ADS.P1)
chan3 = AnalogIn(ads1, ADS.P2, ADS.P3)
chan4 = AnalogIn(ads2, ADS.P0, ADS.P1)
chan5 = AnalogIn(ads2, ADS.P2, ADS.P3)
chan6 = AnalogIn(ads3, ADS.P0, ADS.P1)
#singular analog read
chan7_1_sing = AnalogIn(adc3, ADS.P2)
chan7_2_sing = AnalogIn(adc3, ADS.P3)

c0 = AnalogIn(adc0, ADS.P0, ADS.P1)
c1 = AnalogIn(adc0, ADS.P2, ADS.P3)
c2 = AnalogIn(adc1, ADS.P0, ADS.P1)
c3 = AnalogIn(adc1, ADS.P2, ADS.P3)
#singular analog read
c4_1_sing = AnalogIn(adc2, ADS.P0)
c4_2_sing = AnalogIn(adc2, ADS.P1)
#differential connection read
c5 = AnalogIn(adc2, ADS.P2, ADS.P3)
c6 = AnalogIn(adc3, ADS.P0, ADS.P1)
c7 = AnalogIn(ads3, ADS.P2, ADS.P3)
#import numpy for NaN
import numpy as np

#initialize ADC voltages in case of failure

def getData(): #main function that calls on all other functions to generate data list
#read w1 water temp sensor
    temp = getWTemp()
    
    try:
    #read soil moisture sensor
        moisture_0_raw = chan7_1_sing.voltage*1000 #in mV
        moisture_1_raw = chan7_2_sing.voltage*1000 #in mV
        moisture_0 = getVWC(chan7_1_sing.voltage)
        moisture_1 = getVWC(chan7_2_sing.voltage)
        
    #define readings from ADC
        #pH = -5.82*chan.voltage + 22.1 #calibrated equation
        v0 = chan0.voltage*1000
        v1 = chan1.voltage*1000
        v2 = chan2.voltage*1000
        v3 = chan3.voltage*1000
        v4 = chan4.voltage*1000
        v5 = chan5.voltage*1000
        v6 = chan6.voltage*1000
        
        v_0 = c0.voltage*1000
        v_1 = c1.voltage*1000
        v_2 = c2.voltage*1000
        v_3 = c3.voltage*1000
        #v_4 = c4.voltage*1000 #sacrificed for O2 sensor thermistors
        v_5 = c5.voltage*1000
        v_6 = c6.voltage*1000
        v_7 = c7.voltage*1000
        
        o2_0_raw = c4_1_sing.voltage
        o2_1_raw = c4_2_sing.voltage
        v0_anode_o2 = readO2([o2_0_raw, v_5, 52.8766, 22.486]) #thermistor reading in volts and differential oxygen reading in mV
        v3_anode_o2 = readO2([o2_1_raw, v_6, 52.1266, 22.491]) #thermistor reading in volts and differential oxygen reading in mV
        
    except IOError as e:
        print(e)
        moisture_0_raw = 9999 #in mV
        moisture_1_raw = 9999 #in mV
        moisture_0 = 9999
        moisture_1 = 9999
#define readings from ADC
#pH = -5.82*chan.voltage + 22.1 #calibrated equation
        v0 = 9999
        v1 = 9999
        v2 = 9999
        v3 = 9999
        v4 = 9999
        v5 = 9999
        v6 = 9999

        v_0 = 9999
        v_1 = 9999
        v_2 = 9999
        v_3 = 9999
        #v_4 = c4.voltage*1000 #sacrificed for O2 sensor thermistors
        v_5 = 9999
        v_6 = 9999
        v_7 = 9999
        o2_0_raw = 9999
        o2_1_raw = 9999
        v0_anode_o2 = 9999
        v3_anode_o2 = 9999
    
    
    
    #read oxygen sensor
    #therm_raw = chan8_sing.voltage #in volts
    #therm_raw, o2_v, mVc, Tc (last two are calibration values)
    
    ##Error thrown on 175 sometimes!!
    
#read air temp and air humidity
    #atemp, hum = getDHT()#dht.read_retry(dht.DHT22, DHT)
    #if hum == np.nan or atemp == np.nan:
     #   hum, atemp = last_hum, last_atemp
    last_distance = 1000000
    distance = getDistance(last_distance)
    #make sure distance is the last value on this list
    hum = 9999#chan2.voltage
    P0 = v0*(v0/2000)
    P1 = v1*(v1/2000)
    P2 = v2*(v2/2000)
    P3 = v3*(v3/2000)
    P4 = v4*(v4/2000)
    P5 = v5*(v5/2000)
    P6 = v6*(v6/2000)
    
    p_0 = v_0*(v_0/2000)
    p_1 = v_1*(v_1/2000)
    p_2 = v_2*(v_2/2000)
    p_3 = v_3*(v_3/2000)
    #p_4 = v_4*(v_4/2000)
    p_5 = v_5*(v_5/2000)
    p_6 = v_6*(v_6/2000)
    p_7 = v_7*(v_7/2000)
    GPIO.output(25, GPIO.LOW)
    VWC_TEROS, temp_TEROS, EC, matric_pot_0, matric_pot_1 = readTEROS()
    
    return [v0, v1, v2, v3, v4, v5, v6, v_0, v_1, v_2, v_3, v_7,
            P0, P1, P2, P3, P4, P5, P6, p_0, p_1, p_2, p_3, p_7,
            temp, moisture_0, moisture_0_raw, moisture_1, moisture_1_raw,
            VWC_TEROS, temp_TEROS, EC, matric_pot_0, matric_pot_1, v0_anode_o2, v3_anode_o2
            ]

#EC-5 sensor:
def getVWC(voltage):
    moisture_raw = voltage*1000
    #calibrated value
    VWC = 0.0000000081*(moisture_raw**3) - 0.0000175897*(moisture_raw**2) + 0.0131376197*moisture_raw - 3.0743960987
    VWC = VWC * 100 #convert to percents
    return VWC

#TEROS sensors, 3 of them:
def readTEROS():
    ser.reset_input_buffer()
    while True:
        ser.write(b"data\n")
        data = ser.readline().decode('utf-8').rstrip().replace('-','+-').replace('\r', '+').split('+')
        #print(data)
        if len(data) == 10: #change this number depending on how many sensors/what type
            raw_data = [float(x) for x in data] #[sensor0_id, VWC_adc_count, temp0, EC, sensor1_id, water_potential1, temp1, sensor2_id, water_potential2, temp2]
            VWC = (1.147e-9)*raw_data[1]**3 - (8.638e-6)*raw_data[1]**2 + (2.187e-2)*raw_data[1] - 1.821e1
            return([VWC, raw_data[2], raw_data[3], raw_data[5], raw_data[8]]) #[VWC(%), temp0(C), EC(μS/cm normalized to 25C), water_potential_0(kPa), water_potential_1(kPa)]

def readO2(sensor):
    #unpack sensor readings here
    therm_raw, o2_v, mVc, Tc = sensor
    Rt = 24900*(2.494/therm_raw -1) #2.494v excitation signal for thermistor, might change if it's not 2.494v
    A = 1.129241e-3
    B = 2.341077e-4
    C = 8.775468e-8
    Ts = 1/(A+B*math.log(Rt)+C*(math.log(Rt))**3) - 273.15 #in Celsius
    #print("O2 temp, mVc: " + str(Ts) + ", " + str(mVc))
    #Pb = 101.35 #barometric pressure in kPa, used for absolute concentration
    mV0 = 3 #mV, estimated for SO-100 series sensors
    #CF = 0.295*Pb/(mVc-mV0) #kPa O2/mV, absolute concentration
    CF = 20.95/(mVc - mV0) #% O2/mV, relative concentration
    offset = CF*mV0
    O2M = CF*o2_v - offset
    C1 = -6.949e-2
    C2 = 1.422e-3
    C3 = -8.213e-7
    C0 = -(C3*(Tc**3)+C2*(Tc**2)+C1*Tc)
    O2 = O2M + C3*Ts**3 + C2*Ts**2 + C1*Ts + C0 #unit of % O2, relative level
    return O2

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
        return getWTemp() #rerun function again'''
'''        
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
'''
def getDistance(last_distance): #output distance in cm
    #setup distance sensing stuff
    # tof.change_address(0x32)
    return 99999999
    '''
    tof.open()
    # Start ranging
    tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)

    timing = tof.get_timing()
    if timing < 20000:
        timing = 20000
    #print("Timing %d ms" % (timing/1000))

    distance = tof.get_distance()

    tof.stop_ranging()
    tof.close()
    if distance > 0:
        return distance/10 #return distance in cm
    else:
        return 9999999'''
'''
from time import sleep
from datetime import datetime
while True:
     print('updating...')
     
     #print(len(getData()))
     #getData()
     print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"),getData())
     sleep(1)'''