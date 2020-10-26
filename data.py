import random
import sqlite3
import numpy as np
from datetime import datetime
from time import sleep
import os

class Logger:
    def __init__(self,tgt_path,database):
        self.data_dict = {}
        self.name_dict = {}# REPLACE FOR TABLEDICT
        self.table_dict = {}
        self.dbtables = []
        self.dbname = database
        
        #date timestamp of the format "_MM_DD_YYYY" for use in table = 'DAILY'
        self.datef = "_" + datetime.now().strftime("%m/%d/%Y").replace("/","_")

        #change to target directory
        os.chdir(tgt_path)

        ## INITIALIZING DATABASE
        #first, keeping note of whether a database exists yet in the directory
        #(to print an alert later) 
        newdb = not os.path.isfile(self.dbname)
        #sqlite connection and cursor... (this will make a new database dbname.db if none exists)
        self.conn = sqlite3.connect(self.dbname)
        self.c = self.conn.cursor()

        #SCANNING THE DATABASE
        #Getting a list of the current tables
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for n in self.c.fetchall():
            self.dbtables.append(n[0])

        #Create an alert for when a new database is being made
        if newdb:
            print('ALERT: No prior database named ' + self.dbname + '. Created a new database in the target directory')

        self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in self.c.fetchall():
            #print(table[0])
            #c.execute(f'PRAGMA table_info({table[0]})')
            self.table_dict[table[0]] = ((),()) #TO DO: READ EXISTING COLUMN NAMES AND TYPES

    def table(self,newtable):
        #check that the length of the column names == length of the column types
        if type(newtable).__name__=="dict":
            for a,b in newtable.items():
                if len(b[0]) != len(b[1]):
                    print('ALERT: table {a} has a different number of column names and column types')
        #elif list(newtable.keys())[0] == 'DAILY':
        #    # implement DAILY TABLE!
        else:
            print('ALERT: You must input a table dictionary')
        ## MAKING A TABLE IF IT DOESN'T EXIST
        #translating datatypes from python to sqlite3
        types = {   "int":"""INTEGER""","float":"""REAL""",
                    "float64":"""REAL""","str":"""TEXT""",
                    "datetime":"""REAL""", "INTEGER":"""INTEGER""",
                    "REAL":"""REAL""","TEXT":"""TEXT"""}
        
        #generating a string for table generation (LOOPING OVER EACH DICTIONARY ITEM)
        for table,info in newtable.items():
            
            names = """("""
            i = 0 #index
            for name in info[0]: #looping over the table names for this table
                key = info[1][i] #getting the datatype for translation via the types dictionary
                names += "{} {},".format(name, types[key])
                #names += """{name} {types[key]}, """
                i += 1
            names = names[:-2] + """)""" #deletes the last ', ' and adds ')'
            
            #Create table if not yet defined, with the following columns...
            self.c.execute("""CREATE TABLE IF NOT EXISTS """ + table + names)

            # add table(s) to the table dictionary...
            self.table_dict[table] = info

    def collect_data(self,table,dataget,tsamp=0,nsamp=1):
        #daily table mode 
        if table == 'DAILY':
            table = self.datef

        #time-controlled data collection 
        # (Running average. tsamp = time between measurements, nsamp = number of measurements)
        
        #data is stored in a numpy array...
        leng = len(dataget())
        data_arr = np.zeros((1,leng))   #initialize the array w/out timestamp (is this line problematic?)
        ct = 0
        while ct < nsamp:
            tup_arr = np.asarray([dataget()]) #put the getdata() into array form
            data_arr = np.append(data_arr, tup_arr, axis=0) #append as new row in the array
            ct += 1
            sleep(tsamp)

        #averaging the columns of the array
        data_avg = tuple(data_arr.sum(axis=0)/nsamp)

        #adding the timestamp
        data_log = (datetime.now().strftime("%m/%d/%Y %H:%M:%S"),) + data_avg
        print(data_log)

        #assign data to tables in data_dict
        if table not in self.data_dict:
            self.data_dict[table] = []
        self.data_dict[table].append(data_log)


    def log_data(self):
        
        ## LOGGING
        for tbl, data in self.data_dict.items(): #FOR ALL DATA IN DICT
            for rdg in data:
                cnt = len(rdg) - 1
                params = '?' + ',?'*cnt
                self.c.execute("INSERT INTO {} VALUES({})".format(tbl, params),rdg) #pushes values into database (dictionary format)
                self.conn.commit()
        
        #empty the data dictionary
        self.data_dict = {}

    def close(self):
        #close sqlite connection
        self.conn.close()
    
    def commit(self):
        #commit sqlite transaction
        self.conn.commit()
    
class Reader:
    def __init__(self,tgt_path,database):
        self.dbname = database

        #change to target directory
        os.chdir(tgt_path)

        ## INITIALIZING DATABASE
        #first, keeping note of whether a database exists yet in the directory
        newdb = not os.path.isfile(self.dbname)
        
        #Create an alert for when a new database is being made
        if newdb:
            print('ALERT: No prior database named ' + self.dbname + '. Created a new database in the target directory')

        #sqlite connection and cursor
        self.conn = sqlite3.connect(self.dbname)
        self.c = self.conn.cursor()

    def table_vals(self,table):
        #Query the database...
        self.c.execute("""SELECT * FROM """ + table)
        
        #return a list...
        return self.c.fetchall()
        #print(self.c.fetchall())
    
    def get_timeset(self,table,num = 1,timeval = None):
        self.c.execute("SELECT * FROM {} ORDER BY time DESC LIMIT {}".format(table, num))
        return self.c.fetchall()
        #print(self.c.fetchall())

    def close(self):
        #close sqlite connection
        self.conn.close()
        
    def commit(self):
        #commit sqlite transaction
        self.conn.commit()
