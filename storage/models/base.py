from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import Column, ForeignKey, INTEGER, MetaData
from sqlalchemy.dialects.postgresql import TEXT, TIMESTAMP, FLOAT, ARRAY, JSON
from sqlalchemy.orm import synonym

from storage import DeclarativeBase


class BaseTable(DeclarativeBase):
    __abstract__ = True

    id = Column(
        INTEGER,
        primary_key=True,
        # server_default=func.gen_random_uuid(),
        # unique=True,
        doc="Unique index of element (type UUID)",
    )
    created = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        doc="Date and time of create (type TIMESTAMP)",
    )
    updated = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        # onupdate=func.current_timestamp(),
        nullable=False,
        doc="Date and time of last update (type TIMESTAMP)",
    )

    def __repr__(self):
        columns = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return f'<{self.__tablename__}: {", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'


