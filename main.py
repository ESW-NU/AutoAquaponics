from time import sleep
import csv
from multiprocessing import Process

global IS_ALIVE
IS_ALIVE = True
    
testfile_name = "test4.csv"

# Set your own file path & config path in file setup.json
# or as environment variables AQUA_testfile_dir, AQUA_config_file
_config_file = None
_testfile_dir = None

def _load_setting_json(json_file_str, json_var):
    from os import path
    from json import load as json_load
    result = None
    if path.exists(json_file_str) and path.isfile(json_file_str):
        with open(json_file_str, 'r') as json_file:
            result = json_load(json_file).get(json_var)
    return result

# Set your own file path & config path in file setup.json
# or as environment variables AQUA_testfile_dir, AQUA_config_file
def load_setting(envir_var: str, setup_file: str, json_var: str, default_return_value: str):
    from os import environ
    yield environ.get(envir_var)
    yield _load_setting_json(setup_file, json_var)
    yield default_return_value

_config_file = None
_testfile_dir = None
def user_settings():
    from os import path
    for config_path_location in load_setting("AQUA_config_file", "setup.json", "config_file", "./config.csv"):
        if config_path_location != None:
            _config_file = config_path_location
            break
    for test_path_location in load_setting("AQUA_testfile_dir", "setup.json", "testfile_dir", "./"):
        if test_path_location != None:
            _testfile_dir = test_path_location
            _testfile_path = path.join(test_path_location, testfile_name)
            break
    if not path.exists(_config_file):
        with open(_config_file, "a+") as _:
            pass  
    return _config_file, _testfile_path

def start_GUI():
    import GUI

def start_data_logging():
    from DataLogger import DataLogger
    DataLogger()

if(__name__ == '__main__'):
    p1 = Process(target=start_data_logging)
    p1.daemon = True
    p2 = Process(target=start_GUI)
    p2.daemon = True
    #start data logging
    p1.start()
    
    config_file, testfile_path = user_settings() #will not need this....
    from os import path
    if not path.exists(testfile_path):
        with open(testfile_path, "a+") as _:
            pass
    
    #start GUI
    p2.start()
    p1.join()
    p2.join()
