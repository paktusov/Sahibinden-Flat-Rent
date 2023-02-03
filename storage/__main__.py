# from storage.connection.mongo import db
from sqlalchemy import delete

from storage.connection.postgres import db
from storage.models import Ad, Price, DataAd, Area, Town, Subscriber, TelegramPost
from storage import DeclarativeBase


class Storage:
    def __init__(self, table: DeclarativeBase):
        self.db = db
        self.table = table

    def find_many(self, find_filters: dict | None = None, sort_filters: str | None = None) -> list:
        rows = self.table.query.filter_by(**find_filters)
        if sort_filters:
            rows = rows.order_by(sort_filters)
        return rows.all()

    def find_one_by_id(self, _id: str) -> dict:
        return self.table.query.filter(self.table.id == _id).first()

    def find_one_by_id_and_replace(self, _id: str, new_object: dict) -> None:
        query = delete(self.table).where(self.table.id == _id)
        self.db.execute(query)
        self.db.flush()
        new_row = self.table(**new_object)
        self.db.add(new_row)
        self.db.commit()

    def find_one_by_id_and_update(self, _id: str, new_fields: dict) -> None:
        current_row = self.table.query.filter(self.table.id == _id).first
        for field, value in new_fields:
            current_row.__dict__[field] = value
        self.db.commit()

    def insert_one(self, new_object: dict) -> None:
        new_row = self.table(**new_object)
        self.db.add(new_row)
        self.db.commit()


ads_table = Storage(table=Ad)
towns_table = Storage(table=Town)
areas_table = Storage(table=Area)
dataad_table = Storage(table=DataAd)
prices_table = Storage(table=Price)
subscribers_table = Storage(table=Subscriber)
telegram_posts_table = Storage(table=TelegramPost)
