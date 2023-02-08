from datetime import datetime

from sqlalchemy import delete

from storage.connection.postgres import db
from storage.models import Ad
from storage import DeclarativeBase
from storage.models.base import BaseTable


class Storage:
    def __init__(self, table: DeclarativeBase):
        self.db = db
        self.table = table
        self.query = self.db.query(self.table)

    def commit(self):
        self.db.commit()

    def find_many_by_ids(self, ids: list | None = None, sort_filters: str | None = None) -> list:
        query = self.query
        if ids:
            query = query.where(self.table.id.in_(ids))
        if sort_filters:
            query = query.order_by(self.table.__dict__[sort_filters])
        return query.all()

    def find_many_by_time(self, time: datetime, sort_filters: str | None = None):
        query = self.query.where(Ad.last_seen >= time, Ad.removed is False)
        for field, value in sort_filters.items():
            query = query.where(Ad.__dict__[field] == value)
        return query.all()

    def find_one(self, _id: str | None = None, sort_filters: str | None = None) -> BaseTable:
        query = self.query
        if _id:
            query = query.where(self.table.id == _id)
        if sort_filters:
            query = query.order_by(self.table.__dict__[sort_filters])
        return query.first()

    def update_one_by_id(self, _id: str, updatable_fields: dict) -> None:
        current_row = self.query.where(self.table.id == _id).first()
        for field, value in updatable_fields.items():
            setattr(current_row, field, value)

    def find_one_by_id_and_replace(self, _id: str, new_object: dict) -> None:
        query = delete(self.table).where(self.table.id == _id)
        self.db.execute(query)
        self.db.flush()
        new_row = self.table(**new_object)
        self.db.add(new_row)
        self.db.commit()

    def find_one_by_id_and_update(self, _id: str, new_fields: dict) -> None:
        current_row = self.table.query.filter(self.table.id == _id).first()
        for field, value in new_fields:
            current_row.__dict__[field] = value
        self.db.commit()

    def insert_one(self, data: dict) -> None:
        fields = set(self.table.__dict__)
        new_object = self.table(**{k: v for k, v in data.items() if k in fields})
        self.db.add(new_object)
        #
        # new_row = self.table(**new_object)
        # self.db.add(new_row)
        # self.db.commit()
