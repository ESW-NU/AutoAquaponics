from time import sleep
import csv
from fakeDataLogger import fakeDataLogger
from multiprocessing import Process
global IS_ALIVE
IS_ALIVE = True

def start_GUI():
    import GUI

def start_data_logging():
    fakeDataLogger("test2.csv")

if(__name__ == '__main__'):
    p1 = Process(target=start_data_logging)
    p1.daemon = True
    p2 = Process(target=start_GUI)
    p2.daemon = True
    #start data logging
    p1.start()
    #create CSV file if it doesn't already exist
    file_name = "/Users/Bill Yen/Desktop/NU Urban Ag/test2.csv"
    create_file = open(file_name, "a+")
    create_file.close()
    #check length of CSV and wait for data logger to populate if it's too small
    input_file = open(file_name, "r")
    reader_file = csv.reader(input_file)
    dataLen = len(list(reader_file))
    if dataLen < 2:
        sleep(10.1)
    input_file.close()
    #start GUI
    p2.start()
    p1.join()
    p2.join()