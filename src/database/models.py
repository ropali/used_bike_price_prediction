from .db import DB


class BikeModel(DB):

    TABLE_NAME = 'bikes'

    def __init__(self):
        super().__init__()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bikes (model_name TEXT, model_year VARCHAR(4), kms_driven VARCHAR(20), owner VARCHAR(10), location VARCHAR(60), mileage VARCHAR(20), power VARCHAR(20) ,price VARCHAR(20))")

        self.con.commit()

    def save(self, data):
        self.insert(
            f"INSERT INTO {self.TABLE_NAME} VALUES (:model_name,:model_year,:kms_driven,:owner,:location,:mileage,:power,:price)", data)

    def all(self, **kwargs):
        return self.find_all(f"select * from {self.TABLE_NAME}")


class UrlVisited(DB):

    TABLE_NAME = 'visted'

    def __init__(self):
        super().__init__()
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (link TEXT)")

        self.con.commit()

    def save(self, data):
        self.insert(
            f"INSERT INTO {self.TABLE_NAME} VALUES (:link)", data)

    def all(self, **kwargs):
        return self.find_all(f"select * from {self.TABLE_NAME}")

    def find(self,link):
        self.cursor.execute(f"SELECT * FROM {self.TABLE_NAME} WHERE link=:link",{'link':link})
        return self.cursor.fetchone()
