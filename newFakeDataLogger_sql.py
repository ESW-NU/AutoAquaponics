from random import choice
import sqlite3
import random
from datetime import datetime
from time import sleep
import os

cwd0 = os.getcwd()
tgt_dir = "C:/Users/markg/Repositories/AutoAquaponics" 
db_name = 'database.db'
tablename = datetime.now().strftime("%m/%d/%Y")

class Logger:
    def __init__(self,tgt_path,database):
        self.data_dict = {}
        self.dbname = database
        #change to target directory
        os.chdir(tgt_path)

    def collect_data(self):
        #collect data and assign to class variable
        choice = [2.322,2.444,2.533,2.666]
        self.data_dict['table1'] = (datetime.now(), random.choice(choice),random.choice(choice),
                                                    random.choice(choice),random.choice(choice),
                                                    random.choice(choice),random.choice(choice),
                                                    random.choice(choice),random.choice(choice),
                                                    random.choice(choice),random.choice(choice)) #TO DO: make this less janky haha
        print(self.data_dict)

    def log_data(self):
        #INITIALIZING DATABASE
        #first, keeping note of whether a database exists yet in the directory
        if os.path.isfile(self.dbname):
            newdb = False
        else:
            newdb = True 
        #sqlite connection and cursor...
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()
        #if doesnt exist, create a table "pH" with three floating pt. ("Real") values for a timestamp and two voltages
        if newdb:
            print('ALERT: No prior database named ' + self.dbname + '. Created a new database in the target directory')
            c.execute("""CREATE TABLE table1(time REAL, pH REAL, 
                                            Water_Temp REAL, Air_Temp REAL, 
                                            Nitrate REAL, TDS REAL, DO REAL, 
                                            Ammonia REAL, Phosphate REAL, 
                                            Humidity REAL, Flow_rt REAL) """)
        
        #pushing values into the db
        for table, data in self.data_dict.items():
            cnt = len(data) - 1
            params = '?' + ',?'*cnt
            c.execute(f"INSERT INTO {table} VALUES({params})",data) #pushes values into database (dictionary format)
            conn.commit()

        #close sqlite connection
        conn.close()
    

def main():

    #this would be a while True for the real logger, with 
    while True:
        logger = Logger(tgt_dir,'database.db')
        logger.collect_data()
        logger.log_data()
        sleep(5)

main()
