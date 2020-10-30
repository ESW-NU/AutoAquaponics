#importing/initializing for plotting/saving
all_we_got_now = ('time', 'pH', 'TDS', 'humidity', 'air_temp', 'water_temp')
now_data_types = ("datetime", "float", "float", "float", "float", "float")

tgt_dir = "C:\\Users\\Bill Yen\\Desktop\\NU Urban Ag\\AutoAquaponics\\" #"/home/pi/AutoAquaponics/databases/" 
db_name = 'sensor_testdb.db'

def data_fxn():
    import numpy as np
    N = len(all_we_got_now)
    return tuple(np.random.randint(0,10,size=(N-1))) #N-tuple of random ints from 0 to 10.

def DataLogger():
    from data import Reader, Logger
    from getData import getData
    sensor_plot_table = {'SensorData':(all_we_got_now, now_data_types)}
    logger = Logger(tgt_dir, db_name)
    logger.table(sensor_plot_table)
    while True:
        logger.collect_data("SensorData", data_fxn, tsamp=5, nsamp=1)
        logger.log_data()
        logger.commit()
        
#DataLogger()