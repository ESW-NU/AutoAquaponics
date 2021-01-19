from time import sleep
import csv
from multiprocessing import Process
import sendtext
import sendemail

# Set your own file path & config path in file setup.json
# or as environment variables AQUA_testfile_dir, AQUA_config_file, AQUA_img_path
_config_file = "setup.json"
_tgt_db_dir = None
_tgt_img_path = None

def _load_setting_json(json_file_str, json_var):
    from os import path
    from json import load as json_load
    result = None
    if path.exists(json_file_str) and path.isfile(json_file_str):
        with open(json_file_str, 'r') as json_file:
            result = json_load(json_file).get(json_var)
    return result

# Set your own config path & database path in file setup.json
# or as environment variables AQUA_tgt_db_dir, AQUA_config_file, AQUA_img_path
def load_setting(envir_var: str, setup_file: str, json_var: str, default_return_value: str):
    from os import environ
    yield environ.get(envir_var)
    yield _load_setting_json(setup_file, json_var)
    yield default_return_value

def user_settings(): 
    from os import path
    for config_path_location in load_setting("AQUA_config_file", "setup.json", "config_file", "./config.csv"):
        if config_path_location != None:
            _config_file = config_path_location
            break
    for db_path_location in load_setting("AQUA_tgt_db_dir", "setup.json", "db_dir", "./"):
        if db_path_location != None:
            _tgt_db_dir = db_path_location
            break
    for img_path_location in load_setting("AQUA_img_path", "setup.json", "img_path", "./"):
        if img_path_location != None:
            _tgt_img_path = img_path_location
            break
    if not path.exists(_config_file):
        with open(_config_file, "a+") as _:
            pass  
    return _config_file, _tgt_db_dir, _tgt_img_path

def start_GUI():
    import GUI

def start_data_logging():
    from DataLogger import DataLogger
    DataLogger()

def emailSender():
    sendemail.sendEmail(user_settings) #figure out the arguments because settings

if(__name__ == '__main__'):
    p1 = Process(target=start_data_logging)
    p1.daemon = True
    p2 = Process(target=start_GUI)
    p2.daemon = True
    p3 = Process(target=emailSender)
    p3.daemon = True
    #start data logging
    p1.start()
    print("Loading Data...")

    p2.start()
    p3.start()
    #start GUI
    p1.join()
    p2.join()
    p3.join()
