# Prototype for logging sensor data
### DataLogger.py has the following data logging functionality so far
1. Record raw voltage of pH and temperature sensor from getData.py every second
2. Take the average of the respective voltages across a 5 seconds span to denoise sensor data
3. Save the denoised pH and temperature sensor data into test.csv every 5 seconds

GUI is the graphical interface that's supposed to eventually display everything with live graphs and buttons to toggle on/off relay controls and allow user to adjust relay timers.
