import random
import sqlite3
import random
from sqlite3.dbapi2 import Error
import numpy as np
from datetime import datetime
from time import sleep
import os

cwd0 = os.getcwd()
tgt_dir = "C:/Users/markg/Repositories/AutoAquaponics" 
db_name = 'testdb.db'

#input data (data coming from outside the logger, to be logged)
data_names = ('time','pH','Water_Temp','Air_Temp','Nitrate','TDS','DO','Ammonia','Phosphate','Humidity','Flow_rt')
choice = [0,1,2,3,4,5,6,7,8,9]
def data_in():
    return (random.choice(choice),random.choice(choice),random.choice(choice),
            random.choice(choice),random.choice(choice),random.choice(choice),
            random.choice(choice),random.choice(choice),random.choice(choice),
            random.choice(choice))

class Logger:
    def __init__(self,tgt_path,database):
        self.data_dict = {}
        self.name_dict = {}
        self.dbtables = []
        self.dbname = database
        
        #date timestamp of the format "_MM_DD_YYYY" for use in table = 'DAILY'
        self.datef = "_" + datetime.now().strftime("%m/%d/%Y").replace("/","_")

        #change to target directory
        os.chdir(tgt_path)

        ## INITIALIZING DATABASE
        #first, keeping note of whether a database exists yet in the directory
        if os.path.isfile(self.dbname):
            newdb = False
        else:
            newdb = True 
        
        #sqlite connection and cursor... (this will make a new database dbname.db if none exists)
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()

        #read table names into the list
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for n in c.fetchall():
            self.dbtables.append(n[0])

        #Create an alert for when a new database is being made
        if newdb:
            print('ALERT: No prior database named ' + self.dbname + '. Created a new database in the target directory')

        # c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # print(c.fetchall())

        #close the connection
        conn.close()

    def table(self,tablename,datanames):
        #sqlite connection and cursor
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()
        

        #close sqlite connection
        conn.close()

    def collect_data(self,table,dataget,datanames,tsamp=0,nsamp=1):
        #daily table mode 
        if table == 'DAILY':
            table = self.datef

        #time-controlled data collection (Running average. tsamp = time between measurements
        #                                                  nsamp = number of measurements)
        #data is stored in a numpy array...
        data_arr = np.zeros((1,len(datanames)-1))   #initialize the array. This doensn't include the timestamp
        ct = 0
        while ct < nsamp:
            tup_arr = np.asarray([dataget()]) #put the getdata() into array form
            print(tup_arr)
            data_arr = np.append(data_arr, tup_arr, axis=0) #append as new row in the array
            ct += 1
            sleep(tsamp)

        #averaging the columns of the array
        data_avg = tuple(data_arr.sum(axis=0)/nsamp)

        #adding the timestamp
        data_log = (datetime.now(),*data_avg)

        #collect data, datanames and assign to data dictionary
        self.data_dict[table] = data_log
        self.name_dict[table] = datanames
        print(self.data_dict)

    def log_data(self,table):
        #daily table
        if table == 'DAILY':
            table = self.datef
        
        #sqlite connection and cursor
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()
        
        ## MAKING A TABLE IF IT DOESN'T EXIST
        #translating datatypes from python to sqlite3
        types = {"int":"""INTEGER""","float":"""REAL""","float64":"""REAL""","str":"""TEXT""","datetime":"""REAL"""}
        
        #generating a string for table generation
        names = """("""
        i = 0 #index
        for name in self.name_dict[table]: #looping over the table names for this table
            key = type(self.data_dict[table][i]).__name__ #getting the datatype for translation via the types dictionary
            names += f"""{name} {types[key]}, """
            i += 1
        names = names[:-2] + """)""" #deletes the last ', ' and adds ')'
        
        #Create table if not yet defined, with the following columns...
        c.execute("""CREATE TABLE IF NOT EXISTS """ + table + names)
        
        ## LOGGING
        for tbl, data in self.data_dict.items():
            cnt = len(data) - 1
            params = '?' + ',?'*cnt
            c.execute(f"INSERT INTO {tbl} VALUES({params})",data) #pushes values into database (dictionary format)
            conn.commit()

        #close sqlite connection
        conn.close()

    def log_data_2(self):
        #sqlite connection and cursor
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()
        
        ## LOGGING
        for tbl, data in self.data_dict.items(): #FOR ALL DATA IN DICT
            cnt = len(data) - 1
            params = '?' + ',?'*cnt
            c.execute(f"INSERT INTO {tbl} VALUES({params})",data) #pushes values into database (dictionary format)
            conn.commit()

        #close sqlite connection
        conn.close()
    
class Reader:
    def __init__(self,tgt_path,database):
        bloop = 0
        self.blep = bloop
        self.dbname = database

        #change to target directory
        os.chdir(tgt_path)

    def read_data(self,table):
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
        
        #Query the database...
        c.execute("""SELECT * FROM """+table)
        
        #return a list...
        print(c.fetchall())
        
        
        #close sqlite connection
        conn.close()

def main():
    #this would be a while True for the real logger, with 
    cnt = 0
    while cnt<5:
        logger = Logger(tgt_dir,db_name)
        logger.collect_data('speedtest',data_in,data_names,tsamp=1,nsamp=5)
        #logger.log_data('speedtest')
        logger.log_data_2()
        cnt = cnt+1
    
    #reader = Reader(tgt_dir,db_name)
    #reader.read_data('_07_28_2020')


main()