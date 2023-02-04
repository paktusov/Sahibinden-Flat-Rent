from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, root_validator


class Area(BaseModel):
    id: str = Field(alias="_id")
    name: str
    is_closed: bool = False
    town_id: str

    @root_validator(pre=True)
    def init_area(cls, values):
        if values.get("id"):
            values["_id"] = values.pop("id")
        return dict(**values)


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



class AdDTO(BaseModel):
    id: str = Field(alias="_id")
    created: datetime
    last_update: datetime
    last_seen: datetime
    thumbnail_url: str = Field(alias="thumbnailUrl", default="")
    price: float
    removed: int = 0
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
        # values['history_price'] = values.get('history_price', [Price(price=values['price'], updated=now)])
        if values.get("id"):
            values["_id"] = values.pop("id")
        return dict(**values)
