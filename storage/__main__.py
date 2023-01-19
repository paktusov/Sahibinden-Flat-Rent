from storage.mongo import db


class Storage:
    def __init__(self, table_name: str):
        self.db = db
        self.table = self.db[table_name]

    def find_one(self, find_filters: dict | None = None) -> dict:
        return self.table.find_one(find_filters)

    def find_many(self, find_filters: dict | None = None, sort_filters: str | None = None) -> list:
        objects = self.table.find(find_filters)
        if sort_filters:
            objects = objects.sort(sort_filters)
        return objects

    def find_one_and_replace(self, find_filters: dict, new_object: dict) -> dict:
        return self.table.find_one_and_replace(find_filters, new_object, upsert=True)

    def find_one_and_update(self, find_filters: dict, new_fild: dict) -> dict:
        return self.table.find_one_and_update(find_filters, new_fild)

    def insert_one(self, new_object: dict) -> dict:
        return self.table.insert_one(new_object)
