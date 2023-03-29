import logging
import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings


load_dotenv()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


class TelegramSettings(BaseSettings):
    token_antalya_bot: str
    antalya_bot_username: str
    antalya_bot_id: str
    id_antalya_channel: str
    id_antalya_chat: str

    class Config:
        evn_file = ".env"
        env_prefix = "telegram_"


class MongoDBSettings(BaseSettings):
    username: Optional[str]
    password: Optional[str]
    uri: str
    port: int
    database: str

    class Config:
        evn_file = ".env"
        env_prefix = "mongodb_"


class PostgresSettings(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DB: str

    class Config:
        evn_file = ".env"
        env_prefix = 'POSTGRES_'

    @property
    def database_uri(self) -> str:
        return f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"


class CelerySettings(BaseSettings):
    broker: str = "redis://redis"
    timezone: str = "Europe/Istanbul"
    worker_max_tasks_per_child: int = 1
    broker_pool_limit: bool = None


class MapboxSettings(BaseSettings):
    token: str
    url: str

    class Config:
        evn_file = ".env"
        env_prefix = "mapbox_"


telegram_config = TelegramSettings()
mongo_config = MongoDBSettings()
celery_config = CelerySettings()
mapbox_config = MapboxSettings()
postgres_config = PostgresSettings()