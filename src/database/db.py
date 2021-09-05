import sqlite3



class DB:

    DB_NAME = 'local.db'

    def __init__(self):
        self.con = sqlite3.connect(self.DB_NAME)
        self.cursor = self.con.cursor()


    def insert(self,query,data=None):
        self.cursor.execute(query,data)
        self.con.commit()
        

    def find_all(self,query,params=()):
        self.cursor.execute(query,params)
        return self.cursor.fetchall()

    

    


    