from sqlalchemy import INTEGER, Column, ForeignKey, MetaData
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT, JSON, TEXT, TIMESTAMP
from sqlalchemy.orm import declarative_base, synonym
from sqlalchemy.sql import func


convention = {
    "all_column_names": lambda constraint, table: "_".join([column.name for column in constraint.columns.values()]),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
DeclarativeBase = declarative_base(metadata=metadata)


class BaseTable(DeclarativeBase):
    __abstract__ = True

    id = Column(
        INTEGER,
        primary_key=True,
        doc="Unique index of element",
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
        nullable=False,
        doc="Date and time of last update (type TIMESTAMP)",
    )

    def __repr__(self):
        columns = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return f'<{self.__tablename__}: {", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'
