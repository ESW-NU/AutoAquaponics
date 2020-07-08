import sqlite3
import random
from datetime import datetime
from time import sleep
loc = "/Users/markg/Repositories/Test Files/" 

class Logger:
    def __init__(self):
        self.data_dict = {}

    def collect_data(self):
        #collect data and assign to class variable
        self.data_dict['pH'] = (datetime.now(), random.choice([2.322,2.444,2.533,2.666]))

    def print_data(self):
        print(self.data_dict['val1'])

    def log_data(self):
        #log the data into a sqlite database 
        conn = sqlite3.connect('datalogger.db')
        cursor = conn.cursor()

        for table, data in self.data_dict.items():
            cnt = len(data) - 1
            params = '?' + ',?'*cnt
            cursor.execute(f"INSERT INTO {table} VALUES({params})",data)
            conn.commit()

        conn.close()
                

def main():
    while True:
        logger = Logger()
        logger.collect_data()
        logger.log_data()
        sleep(5)

main()
