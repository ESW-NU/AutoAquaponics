from DataLogger import DataLogger
from multiprocessing import Process

<<<<<<< HEAD
def start_data_logging():
    DataLogger("test.csv")

def start_GUI():
    import GUI
    

p1 = Process(target=start_data_logging)
p1.start()
p2 = Process(target=start_GUI)
=======
def start_gui():
    import GUI

def start_data_logging():
    DataLogger("test2.csv")

p1 = Process(target=start_gui)
p1.start()
p2 = Process(target=start_data_logging)
>>>>>>> 30031694a7f2d81b2dddf1af7d82381f841cf0ac
p2.start()
p1.join()
p2.join()