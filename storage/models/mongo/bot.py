from pydantic import BaseModel, Field


class TelegramIdAd(BaseModel):
    id: str = Field(alias="_id")
    telegram_channel_message_id: str
    telegram_chat_message_id: str


class SubscriberParameters(BaseModel):
    max_price: list[str] = ["30000"]
    floor: list[str] = ["all"]
    rooms: list[str] = ["all"]
    heating: list[str] = ["all"]
    areas: dict[str, bool] = {"83": True, "84": True, "85": True}
    furniture: list[str] = ["all"]


class Subscriber(BaseModel):
    id: str = Field(alias="_id")
    active: bool = False
    parameters: SubscriberParameters
