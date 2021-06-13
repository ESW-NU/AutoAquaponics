from main import user_settings
#from getData import getData

config_path, db_path, img_path = user_settings()
db_name = 'sensor_db.db'

param_list = ['pH', 'TDS (ppm)', 'Rela. Humidity (%)', 'Air Temp (\N{DEGREE SIGN}C)', 'Water Temp (\N{DEGREE SIGN}C)', 'Water Level (cm)']
all_we_got_now = ('unix_time', 'pH', 'TDS', 'humidity', 'air_temp', 'water_temp', 'distance')
now_data_types = ("datetime", "float", "float", "float", "float", "float", "float")
end_GOAL = ["pH", "TDS (ppm)", "DO (ppm)", "Phosphate (ppm)", "Nitrate (ppm)", "Ammonia (ppm)", "Air Temperature (\N{DEGREE SIGN}C)",
                   "Air Humidity (%)", "Water Temperature (\N{DEGREE SIGN}C)", "Water Level (cm)", "Flow Rate (GPH)"]

def data_fxn(last_distance, last_wtemp):
    import numpy as np
    N = len(all_we_got_now)
    pH = 5
    TDS = 50
    hum = 30
    atemp = 15
    wtemp = 15
    distance = 40
    return pH, TDS, hum, atemp, wtemp, distance #N-tuple of random ints from 0 to 10.

def DataLogger():
    from data import Reader, Logger
    #from getData import getData #comment out if you are testing on computer
    import numpy as np
    sensor_plot_table = {'SensorData':(all_we_got_now, now_data_types)}
    logger = Logger(db_path, db_name)
    logger.table(sensor_plot_table)
    last_distance = np.nan #to give an arbitrary initial value to getData for the first time the distance sensor fails
    last_wtemp = 21 #arbitrary initial value
    last_hum = np.nan
    last_atemp = np.nan
    while True:
        #change getData(last_distance, last_wtemp) to data_fxn(last_distance, last_wtemp) if you are testing on your computer
        last_distance, last_wtemp, last_atemp, last_hum = np.round(logger.collect_data("SensorData", data_fxn(last_distance, last_wtemp), last_distance, last_wtemp, last_hum, last_atemp, tsamp=1, nsamp=5),2) #change tsamp and nsamp for logging time/frequency
        logger.log_data()
        logger.commit()
        
#DataLogger()