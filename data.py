import random
import sqlite3
import random
from datetime import datetime
from time import sleep
import os

cwd0 = os.getcwd()
tgt_dir = "C:/Users/markg/Repositories/AutoAquaponics" 
db_name = 'testdb.db'

#input data (data coming from outside the logger, to be logged)
data_names = ('time','pH','Water_Temp','Air_Temp','Nitrate','TDS','DO','Ammonia','Phosphate','Humidity','Flow_rt')
choice = [2.322,2.444,2.533,2.666]
def data_in():
    return (datetime.now(), random.choice(choice),random.choice(choice),
            random.choice(choice),random.choice(choice),random.choice(choice),
            random.choice(choice),random.choice(choice),random.choice(choice),
            random.choice(choice),random.choice(choice))

class Logger:
    def __init__(self,tgt_path,database):
        self.data_dict = {}
        self.name_dict = {}
        self.dbname = database
        
        #by default (daily table mode), the name of the table is a date timestamp of the format "_MM_DD_YYYY"
        self.datef = "_" + datetime.now().strftime("%m/%d/%Y").replace("/","_")

        #change to target directory
        os.chdir(tgt_path)

    def collect_data(self,table,datain,datanames):
        #daily table mode 
        if table == 'DAILY':
            table = self.datef

        #collect data, datanames and assign to data dictionary
        self.data_dict[table] = datain
        self.name_dict[table] = datanames
        print(self.data_dict)

    def log_data(self,table):
        #daily table
        if table == 'DAILY':
            table = self.datef
        
        ## INITIALIZING DATABASE
        #first, keeping note of whether a database exists yet in the directory
        if os.path.isfile(self.dbname):
            newdb = False
        else:
            newdb = True 
        
        #sqlite connection and cursor... (this will make a new database dbname.db if none exists)
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()
        
        #Create an alert for when a new database is being made
        if newdb:
            print('ALERT: No prior database named ' + self.dbname + '. Created a new database in the target directory')
        
        ## LOGGING
        #translating datatype from python to sqlite3
        types = {"int":"""INTEGER""","float":"""REAL""","str":"""TEXT""","datetime":"""REAL"""}
        
        #generating a string for table generation
        names = """("""
        i = 0 #index
        for name in self.name_dict[table]: #looping over the table names for this table
            key = type(self.data_dict[table][i]).__name__
            names += f"""{name} {types[key]}, """
            i += 1
        names = names[:-2] + """)"""
        
        
        #Create table if not yet defined, with the following columns...
        c.execute("""CREATE TABLE IF NOT EXISTS """ + table + names)
        
        #pushing values into the db
        for tbl, data in self.data_dict.items():
            cnt = len(data) - 1
            params = '?' + ',?'*cnt
            c.execute(f"INSERT INTO {tbl} VALUES({params})",data) #pushes values into database (dictionary format)
            conn.commit()

        #close sqlite connection
        conn.close()
    

def main():
    #this would be a while True for the real logger, with 
    cnt = 0
    while cnt<5:
        logger = Logger(tgt_dir,db_name)
        logger.collect_data('DAILY',data_in(),data_names)
        logger.log_data('DAILY')
        cnt = cnt+1
        
        sleep(1)

main()
