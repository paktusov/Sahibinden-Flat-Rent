from storage.models.base import BaseTable
from sqlalchemy import Column, INTEGER, text
from sqlalchemy.dialects.postgresql import TEXT, SMALLINT, ARRAY, JSON, JSONB


class TelegramPost(BaseTable):
    __tablename__ = "telegram_posts"
    channel_message_id = Column("channel_message_id", INTEGER, nullable=False, doc="Chanel message id")
    chat_message_id = Column("chat_message_id", INTEGER, nullable=False, doc="Chat message id")


class Subscriber(BaseTable):
    __tablename__ = "subscribers"
    active = Column("active", SMALLINT, server_default="0", nullable=False, doc="Subscription status")
    max_price = Column("max_price", ARRAY(TEXT), nullable=True, doc="Max price")
    floor = Column("floor", ARRAY(TEXT), nullable=True, doc="Floor")
    rooms = Column("rooms", ARRAY(TEXT), nullable=True, doc="Rooms")
    heating = Column("heating", ARRAY(TEXT), nullable=True, doc="Heating")
    # areas = Column("areas", JSONB, server_default=text("'{\"83\": \"True\"}'")'{"83": True, "84": True, "85": True}', nullable=False, doc="Areas")
    furniture = Column("furniture", ARRAY(TEXT), nullable=True, doc="Furniture")
