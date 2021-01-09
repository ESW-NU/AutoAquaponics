from main import user_settings

config_path, db_path, img_path = user_settings()
db_name = 'sensor_db.db'

all_we_got_now = ('time', 'pH', 'TDS', 'humidity', 'air_temp', 'water_temp', 'distance')
now_data_types = ("datetime", "float", "float", "float", "float", "float", "float")
end_GOAL = ["pH", "TDS (ppm)", "DO (ppm)", "Phosphate (ppm)", "Nitrate (ppm)", "Ammonia (ppm)", "Air Temperature (\N{DEGREE SIGN}C)",
                   "Air Humidity (%)", "Water Temperature (\N{DEGREE SIGN}C)", "Water Level (cm)", "Flow Rate (GPH)"]

def data_fxn(last_distance, last_wtemp):
    import numpy as np
    N = len(all_we_got_now)
    return tuple(np.random.randint(0,10,size=(N-1))) #N-tuple of random ints from 0 to 10.

def DataLogger():
    from data import Reader, Logger
    #from getData import getData #comment out if you are testing on computer
    import numpy as np
    sensor_plot_table = {'SensorData':(all_we_got_now, now_data_types)}
    logger = Logger(db_path, db_name)
    logger.table(sensor_plot_table)
    last_distance = np.nan #to give an arbitrary initial value to getData for the first time the distance sensor fails
    last_wtemp = 21 #arbitrary initial value
    while True:
        #change getData to data_fxn if you are testing on your computer
        last_distance, last_wtemp = np.round(logger.collect_data("SensorData", data_fxn, last_distance, last_wtemp, tsamp=1, nsamp=5),2) #change tsamp and nsamp for logging time/frequency
        logger.log_data()
        logger.commit()
        
#DataLogger()