import os
import couchdb

class DataBase:
    def __init__(self) -> None:
        couchdb_url = os.getenv('COUCHDB_URL')
        couchdb_username = os.getenv('COUCHDB_USERNAME')
        couchdb_password = os.getenv('COUCHDB_PASSWORD')
        self.db = couchdb.Server(couchdb_url)
        self.db.resource.credentials = (couchdb_username, couchdb_password)
    
    def __getitem__(self, db_name):
        return self.db[db_name]

db = DataBase()