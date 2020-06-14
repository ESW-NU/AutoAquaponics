def getData():
#import necessary modules and initialize I2C bus
    import board
    import busio
    i2c = busio.I2C(board.SCL, board.SDA)
#import board module (ADS1115)
    import adafruit_ads1x15.ads1115 as ADS
#import ADS1x15 library's version of AnalogIn
    from adafruit_ads1x15.analog_in import AnalogIn
#create ADS object
    ads = ADS.ADS1115(i2c)
    ads.gain = 2/3
#single ended mode read for pin 0 and 1
    chan = AnalogIn(ads, ADS.P0)
    chan1 = AnalogIn(ads, ADS.P1)
    return chan.voltage, chan1.voltage
