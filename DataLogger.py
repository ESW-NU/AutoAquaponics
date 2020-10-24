#importing/initializing for plotting/saving
all_we_got_now - ('time', 'pH', 'humidity', 'air temp', 'water temp')
now_data_types = ("datetime", "float", "float", "float", "float")
tgt_dir = "C:\\Users\\Chris\\Desktop\\NU_Urban_Ag" #change to RPi path
db_name = 'sensor_testdb.db'

def DataLogger():
    from data import Reader, Logger
    sensor_plot_table = {'Sensor Data':(all_we_got_now, now_data_types)}
    logger = Logger(tgt_dir, db_name)
    logger.table(sensor_plot_table)
    while True:
        from getData import getData
        Logger.collect_data("Sensor Data", getData, tsamp=60, nsamp=5)
        Logger.log_data()
        Logger.close()