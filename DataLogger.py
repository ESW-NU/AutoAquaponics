#importing/initializing for plotting/saving
def DataLogger():
    #importing data from other function
    from getData import getData    
    from data import Reader, Logger
    # from getData import getData
    Logger.collect_data("Sensor Data", getData, tsamp=60, nsamp=5)
    Logger.log_data()
    Logger.close()