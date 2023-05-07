from getData import getData
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import numpy as np

all_we_got_now = ('unix_time', 'pH', 'TDS', 'humidity', 'air_temp', 'water_temp', 'distance')
cred = credentials.Certificate("./serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)

db = firestore.client()
print(db)
LOG_EVERY = 15

ref = db.collection(u'tolerances').document(u'pH')

def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        docDict = doc.to_dict()
        print(docDict)
        
doc_watch = ref.on_snapshot(on_snapshot)

print(db)
LOG_EVERY = 15

param_list = ['pH', 'TDS (ppm)', 'Rela. Humidity (%)', 'Air Temp (\N{DEGREE SIGN}C)', 'Water Temp (\N{DEGREE SIGN}C)', 'Water Level (cm)']
all_we_got_now = ('unix_time', 'pH', 'TDS', 'humidity', 'air_temp', 'water_temp', 'distance')
now_data_types = ("datetime", "float", "float", "float", "float", "float", "float")
end_GOAL = ["pH", "TDS (ppm)", "DO (ppm)", "Phosphate (ppm)", "Nitrate (ppm)", "Ammonia (ppm)", "Air Temperature (\N{DEGREE SIGN}C)",
                   "Air Humidity (%)", "Water Temperature (\N{DEGREE SIGN}C)", "Water Level (cm)", "Flow Rate (GPH)"]

def data_fxn(last_distance, last_wtemp):
    import numpy as np
    N = len(all_we_got_now)
    pH = 5
    TDS = 50
    hum = 30
    atemp = 15
    wtemp = 15
    distance = 40
    return pH, TDS, hum, atemp, wtemp, distance #N-tuple of random ints from 0 to 10.

def DataLogger():
    #from getData import getData #comment out if you are testing on computer
    distance = np.nan #to give an arbitrary initial value to getData for the first time the distance sensor fails
    wtemp = 21 #arbitrary initial value
    hum = np.nan
    atemp = np.nan
    time_to_log = round(time.time())
    
    while True:
        #change tsamp and nsamp for logging time/frequency
        #use this for RPi with real sensors (comment line below if on computer, also comment line 2)
        # last_distance, last_wtemp, last_atemp, last_hum = np.round(logger.collect_data("SensorData", getData(last_distance, last_wtemp, last_hum, last_atemp), tsamp=1, nsamp=10),2)
        pH, TDS, hum, atemp, wtemp, distance = np.round(getData(distance, wtemp, hum, atemp), 2)
        curr_time = round(time.time())
        if curr_time < time_to_log:
            continue
        data_tuple = (curr_time, pH, TDS, hum, atemp, wtemp, distance)
        #use this to simulate sensor logging data on computer (comment line below if on RPi)
        #last_distance, last_wtemp, last_atemp, last_hum = np.round(logger.collect_data("SensorData", data_fxn(last_distance, last_wtemp), last_distance, last_wtemp, last_hum, last_atemp, tsamp=1, nsamp=5),2)
        # logger.log_data()
        # logger.commit()

        data_dict = {}
        for i in range(len(data_tuple)):
            data_dict[all_we_got_now[i]] = data_tuple[i]
        db.collection(u'stats').add(data_dict)
        time_to_log = curr_time + LOG_EVERY * 60
       
DataLogger()