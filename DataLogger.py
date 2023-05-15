from main import user_settings
#from getData import getData

config_path, db_path, img_path = user_settings()
db_name = 'sensor_db.db'

param_list = ['v0 (mV)', 'v1 (mV)', 'v2 (mV)', 'v3 (mV)', 'v4 (mV)', 'v5 (mV)', 'v6 (mV)', 'v7 (mV)', 'v8 (mV)', 'v9 (mV)', 'v10 (mV)', 'v11 (mV)', 'v12 (mV)', 'v13 (mV)', 'v14 (mV)',
              'p0 (uW)','p1 (uW)', 'p2 (uW)', 'p3 (uW)', 'p4 (uW)', 'p5 (uW)', 'p6 (uW)', 'p7 (uW)', 'p8 (uW)', 'p9 (uW)','p10 (uW)','p11 (uW)','p12 (uW)','p13 (uW)','p14 (uW)',
              'Soil Temp (\N{DEGREE SIGN}C)', 'Soil Moisture (%)', 'Soil Moisture Raw (mV)', 'TEROS Soil Moisture (%)', 'TEROS Temp (C)', 'EC (uS/cm)', 'Matric Potential (kPa)',
              'O2 at v0 depth (%)', 'O2 at v3 depth (%)']
all_we_got_now = ('unix_time', 'v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10', 'v11', 'v12', 'v13', 'v14',
                  'p0','p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13', 'p14',
                  'soil_temp', 'soil_moisture', 'soil_moisture_raw', 'teros_moisture', 'teros_temp', 'EC', 'matric_pot', 'O2_v0', 'O2_v3')
now_data_types = ("datetime", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float",
                  "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float",
                  "float", "float", "float", "float", "float", "float", "float", "float", "float", "float")
#end_GOAL = ["pH", "TDS (ppm)", "DO (ppm)", "Phosphate (ppm)", "Nitrate (ppm)", "Ammonia (ppm)", "Air Temperature (\N{DEGREE SIGN}C)",
#                   "Air Humidity (%)", "Water Temperature (\N{DEGREE SIGN}C)", "Water Level (cm)", "Flow Rate (GPH)"]
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
    from getData import getData #comment out if you are testing on computer
    import numpy as np
    sensor_plot_table = {'SensorData':(all_we_got_now, now_data_types)}
    logger = Logger(db_path, db_name)
    logger.table(sensor_plot_table)
    last_distance = np.nan #to give an arbitrary initial value to getData for the first time the distance sensor fails
    last_wtemp = 21 #arbitrary initial value
    last_hum = np.nan
    last_atemp = np.nan
    while True:
        #change tsamp and nsamp for logging time/frequency
        #use this for RPi with real sensors (comment line below if on computer, also comment line 2)
        last_distance, last_wtemp, last_atemp, last_hum = np.round(logger.collect_data("SensorData", getData(), tsamp=1, nsamp=60),2)
        #use this to simulate sensor logging data on computer (comment line below if on RPi)
        #last_distance, last_wtemp, last_atemp, last_hum = np.round(logger.collect_data("SensorData", data_fxn(last_distance, last_wtemp), last_distance, last_wtemp, last_hum, last_atemp, tsamp=1, nsamp=60),2)
        logger.log_data()
        logger.commit()
        
#DataLogger()