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


class AdDTO(BaseModel):
    id: int
    created: datetime
    updated: datetime
    last_seen: datetime
    thumbnail_url: str = Field(alias="thumbnailUrl", default="")
    price: float
    removed: bool = False
    title: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    attributes: Optional[dict[str, str]]
    url: Optional[str]
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
        now = datetime.utcnow()
        values["updated"] = values.get("last_update", now)
        values["last_seen"] = now
        values["created"] = values.get("created", now)
        return dict(**values)
