from storage.mongo import db


class Storage:
    def __init__(self, table_name: str):
        self.db = db
        self.table = self.db[table_name]

    def find_many(self, find_filters: dict | None = None, sort_filters: str | None = None) -> list:
        objects = self.table.find(find_filters)
        if sort_filters:
            objects = objects.sort(sort_filters)
        return objects

    def find_one(self, _id: str) -> dict:
        return self.table.find_one({"_id": _id})

    def find_one_and_replace(self, _id: str, new_object: dict) -> dict:
        return self.table.find_one_and_replace({"_id": _id}, new_object, upsert=True)

    def find_one_and_update(self, _id: str, new_fild: dict) -> dict:
        return self.table.find_one_and_update({"_id": _id}, new_fild)

    def insert_one(self, new_object: dict) -> dict:
        return self.table.insert_one(new_object)


flats_table = Storage(table_name="flats")
subscribers_table = Storage(table_name="subscribers")
towns_table = Storage(table_name="towns")
areas_table = Storage(table_name="areas")
telegram_posts_table = Storage(table_name="telegram_posts")
