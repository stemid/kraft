from web import database

db = database(dbn='sqlite', db='telldus.db')

def initialize_db():
    db.query('create table Device(name STRING, did INTEGER, house INTEGER, protocol STRING);')

def add_device(name,did,house,protocol):
    try:
        db.insert(name,did,house,protocol)
    except:
        raise
