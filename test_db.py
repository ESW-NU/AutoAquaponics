db_name = 'sensor_db'
db_path = '/media/pi/76E8-CACF/Soil-Power-Data-Backup/'
from data import Reader
reader = Reader(db_path, db_name)
most_recent = reader.query_by_num(table="SensorData", num=1)
#t = reader.table_vals(table="SensorData")
print(most_recent)

'''
import sqlite3

# creating file path
dbfile = db_path+db_name#'/media/pi/76E8-CACF/Soil-Power-Data-Backup/sensor_db'
# Create a SQL connection to our SQLite database
con = sqlite3.connect(dbfile)

# creating cursor
cur = con.cursor()

# reading all table names
table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
# here is you table list
print(table_list)

# Be sure to close the connection
con.close()'''