#importing/initializing for plotting/saving
all_we_got_now = ('time', 'pH', 'humidity', 'air temp', 'water temp')
now_data_types = ("datetime", "float", "float", "float", "float")
tgt_dir = "/home/pi/Desktop/AutoAquaponics-master/databases/"
db_name = 'sensor_testdb.db'

def data_fxn():
    import numpy as np
    N = 5
    return tuple(np.random.randint(0,10,size=(N-1))) #N-tuple of random ints from 0 to 10.

def DataLogger():
    from data import Reader, Logger
    sensor_plot_table = {'Sensor Data':(all_we_got_now, now_data_types)}
    logger = Logger(tgt_dir, db_name)
    logger.table(sensor_plot_table)
    for i in range(20):
        from getData import getData
        Logger.collect_data("Sensor Data", data_fxn, tsamp=1, nsamp=5)
        Logger.log_data()
        Logger.close()