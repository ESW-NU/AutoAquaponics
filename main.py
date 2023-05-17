# main.py
from get_data import get_data
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import numpy as np
from ble import BLE
from ble import FakeBLE
import argparse

parser = argparse.ArgumentParser(description="This script can be run with the following arguments:",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-l', '--logging', const=15, default=15, type=int, help='Data logging frequency (minutes)', nargs='?')
parser.add_argument('-f', '--fake', action="store_true", help='Send fake bluetooth messages rather than real ones')
args = parser.parse_args()
config = vars(args)
LOG_EVERY = config['logging']
REAL_BLE = config['fake']


ble = BLE() if REAL_BLE else FakeBLE()
ble.BLE_init()

all_we_got_now = ('unix_time', 'pH', 'TDS', 'humidity', 'air_temp', 'water_temp', 'distance')
cred = credentials.Certificate("./serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)

db = firestore.client()
LOG_EVERY = 15

names = {
    'lights': ['shelf1', 'shelf2', 'fish-tank', 'basking'],
    'water-pump': ['status', 'bed-A', 'bed-B']
    # add more sensors here in the future; also add documents to firebase
    # 'backwashing': [],
    # 'fish-feeder': []
}

def snap(doc_snapshot, col_name, doc_name):
    doc = doc_snapshot[0].to_dict()

    if col_name == 'lights':
        i = names['lights'].index(doc_name)
        mode = doc['status']
        ble.BLE_lights_mode(i, mode)
        if mode == 'timer':
            ble.BLE_lights_duration(i, doc['starthh'], doc['startmm'], doc['durationhh'], doc['durationmm'], doc['meridiem'])
    
    elif col_name == 'water-pump':
        if doc_name == 'status':
            ble.BLE_pump_mode(doc['status'])
        else:
            ble.BLE_solenoid_interval(doc_name, doc['pumpTime'])


# Event handlers: Add more handlers in the future based on the key/values in names

ref = db.collection('lights').document('shelf1')
doc = ref.on_snapshot(lambda doc_snapshot, changes, read_time: snap(doc_snapshot, 'lights', 'shelf1'))

ref = db.collection('lights').document('shelf2')
doc = ref.on_snapshot(lambda doc_snapshot, changes, read_time: snap(doc_snapshot, 'lights', 'shelf2'))

ref = db.collection('lights').document('fish-tank')
doc = ref.on_snapshot(lambda doc_snapshot, changes, read_time: snap(doc_snapshot, 'lights', 'fish-tank'))

ref = db.collection('lights').document('basking')
doc = ref.on_snapshot(lambda doc_snapshot, changes, read_time: snap(doc_snapshot, 'lights', 'basking'))

ref = db.collection('water-pump').document('status')
doc = ref.on_snapshot(lambda doc_snapshot, changes, read_time: snap(doc_snapshot, 'water-pump', 'status'))

ref = db.collection('water-pump').document('bed-A')
doc = ref.on_snapshot(lambda doc_snapshot, changes, read_time: snap(doc_snapshot, 'water-pump', 'bed-A'))

ref = db.collection('water-pump').document('bed-B')
doc = ref.on_snapshot(lambda doc_snapshot, changes, read_time: snap(doc_snapshot, 'water-pump', 'bed-B'))


def find_next_log_time(x, base):
    maybe = base * round(x/base)
    if maybe < x:
        return maybe + base
    return maybe

def DataLogger():
    distance = np.nan #to give an arbitrary initial value to getData for the first time the distance sensor fails
    wtemp = 21 #arbitrary initial value
    hum = np.nan
    atemp = np.nan
    curr_time = round(time.time())
    time_to_log = find_next_log_time(curr_time, LOG_EVERY * 60)
    
    while True:
        pH, TDS, hum, atemp, wtemp, distance = np.round(get_data(distance, wtemp, hum, atemp), 2)
        curr_time = round(time.time())
        if curr_time <= time_to_log:
            continue
        data_tuple = (curr_time, pH, TDS, hum, atemp, wtemp, distance)
        
        data_dict = {}
        for i in range(len(data_tuple)):
            data_dict[all_we_got_now[i]] = data_tuple[i]
        db.collection(u'stats').add(data_dict)
        time_to_log = find_next_log_time(curr_time, LOG_EVERY * 60)
       
DataLogger()

if REAL_BLE:
    print('\nWARNING: Sending REAL bluetooth messages to ESP32. To send FAKE messages, quit and run `python main.py -f`')
else:
    print('\nWARNING: Sending FAKE BLE messages to ESP32. To send REAL messages, quit and run `python main.py`')