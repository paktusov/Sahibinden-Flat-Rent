import asyncio
import logging
from datetime import datetime

from celery import Celery
from celery.schedules import crontab

from app.processing import processing_data
from config import celery_config
from storage.connection.postgres import postgres_db
from storage.models.postgres.app import Town


logger = logging.getLogger(__name__)

app = Celery("tasks", broker=celery_config.broker)
app.conf.update(
    worker_max_tasks_per_child=celery_config.worker_max_tasks_per_child,
    broker_pool_limit=celery_config.broker_pool_limit,
    timezone=celery_config.timezone,
)

app.conf.beat_schedule = {
    "Parsing Sahibinden": {
        "task": "app.tasks.start_processing",
        "schedule": crontab(minute="*/5"),
    }
}


@app.task
def start_processing() -> None:
    loop = asyncio.get_event_loop()
    town = postgres_db.query(Town).order_by(Town.last_parsing).first()
    logging.info("Start parsing %s", town.name)
    loop.run_until_complete(processing_data({"address_town": town.id}))
    town.last_parsing = datetime.utcnow()
    postgres_db.commit()
