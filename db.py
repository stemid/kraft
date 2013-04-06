import sqlite3 as conn

db = conn.connect('telldus.db')


def initialize_db():
  with db:
    cur = db.cursor()
    cur.execute("CREATE TABLE DeviceT(id INT primary key, name TEXT, dev_id INT)")

def add_device(device_id,name):
  with db:
    cur = db.cursor()
    cur.execute("INSERT INTO DeviceT VALUES(1,%s,%i)") % (name,device_id)


add_device("1","test name")
