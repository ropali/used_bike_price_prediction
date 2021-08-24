import sqlite3



class DB:

    def __init__(self):
        self.con = sqlite3.connect("local.db")

        self.cursor = self.con.cursor()


    def execute(self,query,data=None):
        self.cursor.execute(query,data)

        return self.con.commit()

    


    