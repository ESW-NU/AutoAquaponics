from DataLogger import DataLogger
from multiprocessing import Process


def start_GUI():
    import GUI

def start_data_logging():
    DataLogger("test.csv")

if(__name__ == '__main__'):
    p1 = Process(target=start_GUI)
    p1.daemon = True
    p2 = Process(target=start_data_logging)
    p2.daemon = True

    p1.start()
    p2.start()

    p1.join()
    p2.join()