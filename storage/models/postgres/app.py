from sqlalchemy import INTEGER, Boolean, Column, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT, JSON, TEXT, TIMESTAMP
from sqlalchemy.orm import relationship, synonym

from storage.models.postgres import BaseTable


class Ad(BaseTable):
    __tablename__ = "ads"
    last_seen = Column("last_seen", TIMESTAMP, nullable=False, doc="Last seen date")
    removed = Column("removed", Boolean, nullable=False, server_default="False", doc="Is removed")
    last_condition_removed = Column(
        "last_condition_removed", Boolean, nullable=False, server_default="False", doc="Is removed"
    )
    thumbnailUrl = Column("thumbnail_url", TEXT, nullable=False, doc="Thumbnail url")
    thumbnail_url = synonym("thumbnailUrl")
    prices = relationship("Price")
    title = Column("title", TEXT, doc="Title")
    lat = Column("lat", FLOAT, nullable=True, doc="Latitude")
    lon = Column("lon", FLOAT, nullable=True, doc="Longitude")
    attributes = Column("attributes", JSON, nullable=True, doc="Attributes")
    url = Column("url", TEXT, nullable=True, doc="Url")
    data = relationship("DataAd")
    photos = Column("photos", ARRAY(TEXT), nullable=True, doc="Photos")
    map_image = Column("map_image", TEXT, nullable=True, doc="Map image")
    address_town = Column("address_town", ForeignKey("towns.id"), nullable=True, doc="Identifier of town")


class DataAd(BaseTable):
    __tablename__ = "data_ads"
    ad_id = Column("ad_id", ForeignKey("ads.id"), nullable=False, doc="Identifier of ad")
    district = Column("district", TEXT, nullable=True, doc="District")
    area = Column("area", TEXT, nullable=True, doc="Area")
    creation_date = Column("creation_date", TIMESTAMP, nullable=True, doc="Creation date")
    gross_area = Column("gross_area", TEXT, nullable=True, doc="Gross area")
    net_area = Column("net_area", TEXT, nullable=True, doc="Net area")
    room_count = Column("room_count", TEXT, nullable=True, doc="Room count")
    building_age = Column("building_age", TEXT, nullable=True, doc="Building age")
    floor = Column("floor", TEXT, nullable=True, doc="Floor")
    building_floor_count = Column("building_floor_count", INTEGER, nullable=True, doc="Building floor count")
    heating_type = Column("heating_type", TEXT, nullable=True, doc="Heating type")
    bathroom_count = Column("bathroom_count", TEXT, nullable=True, doc="Bathroom count")
    balcony = Column("balcony", Boolean, nullable=True, doc="Balcony")
    furniture = Column("furniture", Boolean, nullable=True, doc="Furniture")
    using_status = Column("using_status", TEXT, nullable=True, doc="Using status")
    dues = Column("dues", TEXT, nullable=True, doc="Dues")
    deposit = Column("deposit", TEXT, nullable=True, doc="Deposit")


    @property
    def previous_price(self):
        return self.prices[-2].price

    @property
    def last_price(self):
        return self.prices[-1].price

    @property
    def first_price(self):
        return self.prices[0].price

    @property
    def last_price_update(self):
        return self.prices[-1].updated

    @property
    def full_url(self):
        return f"https://sahibinden.com{self.url}"

    @property
    def short_url(self):
        return f"https://www.sahibinden.com/{self.id}"

    def remove(self):
        self.last_condition_removed = False
        self.removed = True


class Price(BaseTable):
    __tablename__ = "prices"
    ad_id = Column("ad_id", ForeignKey("ads.id"), nullable=False, doc="Identifier of ad")
    price = Column("price", FLOAT, nullable=False, doc="Price")


class Town(BaseTable):
    __tablename__ = "towns"
    name = Column("name", TEXT, nullable=False, doc="Name of town")
    last_parsing = Column("last_parsing", TIMESTAMP, doc="Last parsing date")


class Area(BaseTable):
    __tablename__ = "areas"
    name = Column("name", TEXT, nullable=False, doc="Name of area")
    town_id = Column("town_id", ForeignKey("towns.id"), nullable=False, doc="Identifier of town")
    is_closed = Column("is_closed", Boolean, nullable=False, doc="Residence permit opportunity")


class Cookie(BaseTable):
    __tablename__ = "cookies"
    data = Column("data", JSON, nullable=False, doc="Cookies data")


class Header(BaseTable):
    __tablename__ = "headers"
    data = Column("data", JSON, nullable=False, doc="Headers date")
