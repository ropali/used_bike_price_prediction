from .db import DB

class BikeModel:

    table_name = 'bikes'

    def __init__(self):
        self.db = DB()
        self.db.cursor.execute("CREATE TABLE IF NOT EXISTS bikes (model_name TEXT, model_year VARCHAR(4), kms_driven VARCHAR(20), owner VARCHAR(10), location VARCHAR(60), price VARCHAR(20))")

        self.db.con.commit()
    
    def insert(self,data):
        self.db.execute(f"INSERT INTO {self.table_name} VALUES (:model_name,:model_year,:kms_driven,:owner,:location,:price)", data)
        

    def all(self,**kwargs):
        return self.db.execute(f"select * from {self.table_name}")


class VisitedPageModel:
    
    table_name = 'visited_page'

    def __init__(self):
        self.db = DB()
        self.cursor.execute(f"CREATE IF NOT EXISTS TABLE {self.table_name} (url TEXT")

        self.db.con.commit()
    
    def insert(self,data):
        return self.db.execute(f"INSERT INTO {self.table_name} VALUES (:url)", data)

    def all(self,**kwargs):
        return self.db.execute(f"select * from {self.table_name}")