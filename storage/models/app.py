from storage.connection.postgres import db
from storage.models.base import BaseTable
from sqlalchemy import Column, ForeignKey, INTEGER, Integer
from sqlalchemy.dialects.postgresql import TEXT, TIMESTAMP, SMALLINT, FLOAT, ARRAY, JSON
from sqlalchemy.orm import synonym, relationship


class Ad(BaseTable):
    __tablename__ = "ads"
    last_seen = Column("last_seen", TIMESTAMP, nullable=False, doc="Last seen date",)
    thumbnailUrl = Column("thumbnail_url", TEXT, nullable=False, doc="Thumbnail url",)
    thumbnail_url = synonym("thumbnailUrl")
    removed = Column("removed", SMALLINT, nullable=False, server_default="0", doc="Is removed",)
    last_condition_removed = Column(
        "last_condition_removed", SMALLINT, nullable=False, server_default="0", doc="Is removed",
    )
    title = Column("title", TEXT, nullable=True, doc="Title",)
    lat = Column("lat", FLOAT, nullable=True, doc="Latitude",)
    lon = Column("lon", FLOAT, nullable=True, doc="Longitude",)
    attributes = Column("attributes", JSON, nullable=True, doc="Attributes",)
    url = Column("url", TEXT, nullable=True, doc="Url",)
    photos = Column("photos", ARRAY(TEXT), nullable=True, doc="Photos",)
    map_image = Column("map_image", TEXT, nullable=True, doc="Map image",)
    address_town = Column("address_town", ForeignKey("towns.id"), nullable=True, doc="Identifier of town",)
    prices = relationship('Price')

    # @property
    # def last_price(self):
    #     return self.prices[-1]

    def update_from_existed(self, existed: "Ad"):
        self.created = existed.created

        if existed.last_price != self.last_price:
            self.updated = self.last_price_update
        else:
            self.updated = existed.last_update

        if existed.removed:
            self.last_condition_removed = True

    def remove(self):
        self.last_condition_removed = False
        self.removed = True


class Price(BaseTable):
    __tablename__ = "prices"
    price = Column("price", FLOAT, nullable=False, doc="Price",)
    ad_id = Column("ad_id", ForeignKey("ads.id"), nullable=False, doc="Identifier of ad",)


class DataAd(BaseTable):
    __tablename__ = "data_ads"
    district = Column("district", TEXT, nullable=False, doc="District",)
    area = Column("area", TEXT, nullable=False, doc="Area",)
    creation_date = Column("creation_date", TIMESTAMP, nullable=False, doc="Creation date",)
    gross_area = Column("gross_area", TEXT, nullable=False, doc="Gross area",)
    net_area = Column("net_area", TEXT, nullable=False, doc="Net area",)
    room_count = Column("room_count", TEXT, nullable=False, doc="Room count",)
    building_age = Column("building_age", TEXT, nullable=False, doc="Building age",)
    floor = Column("floor", TEXT, nullable=False, doc="Floor",)
    building_floor_count = Column("building_floor_count", INTEGER, nullable=False, doc="Building floor count",)
    heating_type = Column("heating_type", TEXT, nullable=False, doc="Heating type",)
    bathroom_count = Column("bathroom_count", TEXT, nullable=False, doc="Bathroom count",)
    balcony = Column("balcony", SMALLINT, nullable=False, doc="Balcony",)
    furniture = Column("furniture", SMALLINT, nullable=False, doc="Furniture",)
    using_status = Column("using_status", TEXT, nullable=False, doc="Using status",)
    dues = Column("dues", TEXT, nullable=False, doc="Dues",)
    deposit = Column("deposit", TEXT, nullable=False, doc="Deposit",)
    ad_id = Column("ad_id", ForeignKey("ads.id"), nullable=False, doc="Identifier of ad", )


class Town(BaseTable):
    __tablename__ = "towns"
    name = Column("name", TEXT, nullable=False, doc="Name of town",)
    last_parsing = Column("last_parsing", TIMESTAMP, nullable=True, doc="Last parsing date",)


class Area(BaseTable):
    __tablename__ = "areas"
    name = Column("name", TEXT, nullable=False, doc="Name of area",)
    town_id = Column("town_id", ForeignKey("towns.id"), nullable=False, doc="Identifier of town",)
    is_closed = Column("is_closed", SMALLINT, nullable=False, doc="Residence permit opportunity",)
