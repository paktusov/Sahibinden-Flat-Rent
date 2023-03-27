from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, root_validator


class Cookie(BaseModel):
    data: dict


class Header(BaseModel):
    data: dict


class Area(BaseModel):
    id: str = Field(alias="_id")
    name: str
    is_closed: bool = False
    town_id: str

    @root_validator(pre=True)
    def init_area(cls, values):
        if values.get("id"):
            values["_id"] = values.pop("id")
        return {**values}


class Town(BaseModel):
    id: str = Field(alias="_id")
    name: str
    last_parsing: datetime


class DataAd(BaseModel):
    # region: str
    district: str
    area: str
    creation_date: datetime
    gross_area: str
    net_area: str
    room_count: str
    building_age: str
    floor: str
    building_floor_count: int
    heating_type: str
    bathroom_count: str
    balcony: bool
    furniture: bool
    using_status: str
    dues: str
    deposit: str


class Price(BaseModel):
    price: float
    updated: datetime


class Ad(BaseModel):
    id: int = Field(alias="_id")
    created: datetime
    last_update: datetime
    last_seen: datetime
    removed: bool = False
    last_condition_removed = False
    thumbnail_url: str = Field(alias="thumbnailUrl", default="")
    history_price: list[Price] = Field(default_factory=list)
    # telegram_channel_message_id: Optional[str]
    # telegram_chat_message_id: Optional[str]
    title: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    attributes: Optional[dict[str, str]]
    url: Optional[str]
    data: Optional[DataAd]
    photos: Optional[list[str]]
    map_image: Optional[str]
    address_town: Optional[str]

    @property
    def last_price(self):
        return self.history_price[-1].price

    @property
    def first_price(self):
        return self.history_price[0].price

    @property
    def last_price_update(self):
        return self.history_price[-1].updated

    @property
    def full_url(self):
        return f"https://sahibinden.com{self.url}"

    @property
    def short_url(self):
        return f"https://www.sahibinden.com/{self.id}"

    @root_validator(pre=True)
    def init_ad(cls, values):
        now = datetime.now()
        values["last_update"] = values.get("last_update", now)
        values["last_seen"] = now
        values["created"] = values.get("created", now)
        if not values.get("history_price"):
            values["history_price"] = [Price(price=values["price"], updated=now)]
        # values['history_price'] = values.get('history_price', [Price(price=values['price'], updated=now)])
        if values.get("id"):
            values["_id"] = values.pop("id")
        return {**values}

    def update_from_existed(self, existed: "Ad"):
        self.telegram_channel_message_id = existed.telegram_channel_message_id
        self.telegram_chat_message_id = existed.telegram_chat_message_id
        self.created = existed.created
        self.data = existed.data

        if existed.last_price != self.last_price:
            self.history_price = existed.history_price + self.history_price
            self.last_update = self.last_price_update
        else:
            self.history_price = existed.history_price
            self.last_update = existed.last_update

        if existed.removed:
            self.last_condition_removed = True

    def remove(self):
        self.last_condition_removed = False
        self.removed = True
