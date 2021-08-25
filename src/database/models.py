from .db import DB


class BikeModel(DB):

    TABLE_NAME = 'bikes'

    def __init__(self):
        super().__init__()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bikes (model_name TEXT, model_year VARCHAR(4), kms_driven VARCHAR(20), owner VARCHAR(10), location VARCHAR(60), price VARCHAR(20))")

        self.con.commit()

    def save(self, data):
        self.insert(
            f"INSERT INTO {self.TABLE_NAME} VALUES (:model_name,:model_year,:kms_driven,:owner,:location,:price)", data)

    def all(self, **kwargs):
        return self.find_all(f"select * from {self.TABLE_NAME}")


