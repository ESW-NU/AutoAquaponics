# AutoAquaponics Raspberry Pi Code (v1.0)
## Overview
The AutoAquaponics Raspberry Pi (RPi) Python software serves two purposes:
1. Connect to the ESP32 to obtain data from the AutoAquaponics system sensors and log this data to a Google Firebase Firestore Database.
2. Listen to this database for changes made to the control panel, and send bluetooth messages to the ESP32 when changes are detected.

### Running the Program
The program is run by entering `python main.py` in the command line. Additionally, the following optional arguments can be passed:
- **Help:** `-h` or `--help`. See these instructions on the program's optional arguments.
- **Logging Frequency:** `-l <number>` or `--logging <minutes>`, where `<minutes>` is the frequency with which system data is logged to Firebase. For example, `-l 10` will log data to Firebase every 10 minutes. The default logging frequency is 15 minutes if this argument is not used.
- **BLE Message Type:** `-f` or `--fake`. Pass this flag to tell the program to send fake bluetooth messages; otherwise, it will send real bluetooth messages. It does not need to be passed with any numerical arguments.

**Note:** these optional arguments can be passed together, i.e., `python main.py -l 10 -f` will log data every 10 minutes and send fake bluetooth messages.

### Repository Files & Directories

####  `main.py`
This file handles the control flow of the program, including the following:
- Accept and process optional command line arguments
- Initialize connection to Firebase database
- Set up Firebase event listeners which call `ble.py` functions when changes to the Firebase control panel are observed.
- Run `DataLogger()`, which continuously obtains data from `get_data.py` and logs it to Firebase.

#### `get_data.py`
This file contains the `get_data()` function which is called in `main.py`. This function makes several calls to functions which obtain individual sensor data, such as `get_water_temp()` and `get_tds()`.

#### `ble.py`
This file handles all bluetooth messages sent to the ESP32, and is divided into the following classes:
- `ParentBLE`: This class contains the methods that generate bluetooth messages according to the structure established in [project documents](https://docs.google.com/document/d/17H-WvJsHd-YGuLblgH95uoM-LP0ZRlJ7i7fLkkYbfUw/edit?usp=sharing). For example, `BLE_pump_mode` generates the binary message sequence to change a water pump mode between the 'on', 'off', or 'timer' status.
- `BLE`: This class is a subclass of `ParentBLE` and implements the `__init__()`, `BLE_write()`, and `BLE_disconnect()` methods in order to send real bluetooth messages to the ESP32. It is the default class used by `main.py`.
- `FakeBLE`: This class is a subclass of `ParentBLE` and implements the `__init__()`, `BLE_write()`, and `BLE_disconnect()` methods in order print "fake" bluetooth messages to the command line. It does not send any real messages to the hardware, and can be used when the hardware is not ready to accept messages.

#### `packages.txt`
This file provides connection details to the system hardware.

#### `serviceAccountKey.json`
This file provides the connection details used by `main.py` to connect to the project's Firebase database. It is not tracked on GitHub due to security reasons but exists in the root directory on the RPi.

#### `C++` and `flood_growbeds_manual` directory
These directories contains C++ files used by the system electronics to properly operate the hardware.
