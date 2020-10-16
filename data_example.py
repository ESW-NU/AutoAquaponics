import numpy as np #using this just for a fake data function
from data import Logger
"""
Yo yo yo this is an example file for using data.py, and also a test of if it imports right
lets go 'catz

There are two parts to using data.py, the setup and the loop. The loop can be run live, the 
setup can be run just once, and before the loop. I guess you can also just loop everything
but that sounds like a streamlining issue. Or maybe its no big deal. No one really knows!
"""

#SETUP#
"""
Here's what to define first, outside of using data.py...

DATABASE SETUP
tgt_dir: where you need the database to be stored. A string path or path-like object
db_name: name of the database

NEW TABLE SETUP (necessary for making a new table if it doesn't exist yet, but feel free to 
                run anytime just in case)
data_names: tuple of N number of sensor names. length = N
data_types: tuple of corresponding datatypes (expressed as strings) for N sensors. length = N
new_table: a dictionary wrapping of the above information with the table name in the following
           format: {'table_name':(data_names,data_types)}

DATA FUNCTION


"""
#DATABASE SETUP
tgt_dir = "C:/Users/markg/Repositories/AutoAquaponics" #replace for your own system
db_name = 'testdb.db' #name of the database. Include .db

#NEW TABLE SETUP 
data_names = ('time','sensor1','sensor2','sensor3')
data_types = ("datetime","float","float","float")
new_table = {'goopygoop':(data_names,data_types)}
table = 'asswipe' #give your table a fun name
new_table = {table:(data_names,data_types)} 

#INITIALIZE LOGGER OBJECT
logger = Logger(tgt_dir,db_name) 
logger.table(new_table) 

#DATA FUNCTION
"""
Whatever this is, it should be able to be called at any time and return a tuple of length N-1. (Because it
doensnt include the timestamp, which is added inside logger.collect_data)
"""
def data_fxn():
    N = 4
    return tuple(np.random.randint(0,10,size=(N-1))) #N-tuple of random ints from 0 to 10. I'm using N=4 here


#LOOP
"""
LOOP! Everything inside the loop can be run live. Everything before it can just be run once as setup. 
Here I'm using a while loop so it stops after 12 times, but the things inside can loop forever.

Other stuff about the loop...
Assuming everything works, Logger.collect_data() can be run any number of times at any time. It will 
only actually be sent to the database upon running Logger.
"""
cnt = 0
while cnt<12: 
    
    print('new collect')
    logger.collect_data(table,data_fxn,tsamp=.1,nsamp=5)
    
    #logging every 4 collects 
    if (cnt+1) % 4 == 0:
        print('new log')
        logger.log_data()

    cnt = cnt+1

#CLOSE SQL CONNECTION (after the loop)
logger.close()