from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, root_validator


# pylint: disable=duplicate-code
class AdDTO(BaseModel):
    id: int
    created: datetime
    updated: datetime
    last_seen: datetime
    removed: bool = False
    thumbnail_url: str = Field(alias="thumbnailUrl", default="")
    price: float
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
        values["updated"] = now
        values["last_seen"] = now
        values["created"] = now
        return {**values}
