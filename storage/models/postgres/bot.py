from sqlalchemy import INTEGER, Boolean, Column, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TEXT

from storage.models.postgres import BaseTable


class TelegramPost(BaseTable):
    __tablename__ = "telegram_posts"
    ad_id = Column("ad_id", ForeignKey("ads.id"), nullable=False, doc="Identifier of ad")
    channel_message_id = Column("channel_message_id", INTEGER, nullable=False, doc="Chanel message id")
    chat_message_id = Column("chat_message_id", INTEGER, nullable=False, doc="Chat message id")


class Subscriber(BaseTable):
    __tablename__ = "subscribers"
    active = Column("active", Boolean, server_default="False", nullable=False, doc="Subscription status")
    max_price = Column("max_price", ARRAY(TEXT), doc="Max price")
    floor = Column("floor", ARRAY(TEXT), doc="Floor")
    rooms = Column("rooms", ARRAY(TEXT), doc="Rooms")
    heating = Column("heating", ARRAY(TEXT), doc="Heating")
    areas = Column("areas", JSONB, doc="Areas")
    furniture = Column("furniture", ARRAY(TEXT), doc="Furniture")
