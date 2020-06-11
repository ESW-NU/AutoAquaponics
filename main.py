from DataLogger import DataLogger
from multiprocessing import Process

def start_data_logging():
    DataLogger("test.csv")

def start_GUI():
    import GUI
    

p1 = Process(target=start_data_logging)
p1.start()
p2 = Process(target=start_GUI)
p2.start()
p1.join()
p2.join()