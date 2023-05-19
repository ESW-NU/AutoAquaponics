from main import user_settings
#from getData import getData

config_path, db_path, img_path = user_settings()
db_name = 'sensor_db.db'

'''v0, v1, v2, v3, v4, v5, v6, v_0, v_1, v_2, v_3, v_7,
P0, P1, P2, P3, P4, P5, P6, p_0, p_1, p_2, p_3, p_7,
temp, moisture, moisture_raw, VWC_TEROS, temp_TEROS, EC, matric_pot, v0_anode_o2, v3_anode_o2'''

param_list = ['v0 (mV)', 'v1 (mV)', 'v2 (mV)', 'v3 (mV)', 'v4 (mV)', 'v5 (mV)', 'v6 (mV)', 'v7 (mV)', 'v8 (mV)', 'v9 (mV)', 'v10 (mV)', 'v11 (mV)',
              'p0 (uW)','p1 (uW)', 'p2 (uW)', 'p3 (uW)', 'p4 (uW)', 'p5 (uW)', 'p6 (uW)', 'p7 (uW)', 'p8 (uW)', 'p9 (uW)','p10 (uW)','p11 (uW)',
              'Soil Temp (\N{DEGREE SIGN}C)', 'Soil Moisture 0 (%)', 'Soil Moisture 0 Raw (mV)', 'Soil Moisture 1 (%)', 'Soil Moisture 1 Raw (mV)',
              'TEROS Soil Moisture (%)', 'TEROS Temp (C)', 'EC (uS/cm)', 'Matric Potential 0 (kPa)', 'Matric Potential 1 (kPa)',
              'O2 at v0 depth (%)', 'O2 at v3 depth (%)']
all_we_got_now = ('unix_time', 'v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10', 'v11',
                  'p0','p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11',
                  'soil_temp', 'soil_moisture_0', 'soil_moisture_0_raw', 'soil_moisture_1', 'soil_moisture_1_raw', 'teros_moisture', 'teros_temp', 'EC', 'matric_pot_0', 'matric_pot_1', 'O2_v0', 'O2_v3')
now_data_types = ("datetime", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float",
                  "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float",
                  "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float")
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
        last_distance, last_wtemp, last_atemp, last_hum = np.round(logger.collect_data("SensorData", getData(), tsamp=2, nsamp=30),2)
        #use this to simulate sensor logging data on computer (comment line below if on RPi)
        #last_distance, last_wtemp, last_atemp, last_hum = np.round(logger.collect_data("SensorData", data_fxn(last_distance, last_wtemp), last_distance, last_wtemp, last_hum, last_atemp, tsamp=1, nsamp=60),2)
        logger.log_data()
        logger.commit()
        
#DataLogger()