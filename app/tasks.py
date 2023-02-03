import asyncio
import logging
from datetime import datetime

from celery import Celery
from celery.schedules import crontab

from config import celery_config
from storage.__main__ import towns_table

from app.processing import processing_data


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
    town = towns_table.find_many(sort_filters="last_parsing")[0]
    logging.info("Start parsing %s", town["name"])
    parameter = dict(address_town=town["id"])
    loop.run_until_complete(processing_data(parameter))
    towns_table.find_one_by_id_and_update(town["id"], {"last_parsing": datetime.now()})
