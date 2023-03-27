"""data

Revision ID: 3db537ea249a
Revises: e4c729f03f79
Create Date: 2023-03-26 22:55:58.796748

"""
import logging

from alembic import op
import sqlalchemy as sa

from storage.connection.mongo import mongo_db
from storage.connection.postgres import postgres_db
import storage.models.mongo.app as model_mongo_app
import storage.models.postgres.app as model_postgres_app
import storage.models.mongo.bot as model_mongo_bot
import storage.models.postgres.bot as model_postgres_bot
from storage.models.postgres.bot import Subscriber

# revision identifiers, used by Alembic.
revision = '3db537ea249a'
down_revision = 'e4c729f03f79'
branch_labels = None
depends_on = None


def upgrade():
    mongo_cookies = [model_mongo_app.Cookie(**row) for row in mongo_db.cookies.find()]
    for mongo_cookie in mongo_cookies:
        postgres_cookie = model_postgres_app.Cookie(**mongo_cookie.dict())
        postgres_db.add(postgres_cookie)

    mongo_headers = [model_mongo_app.Header(**row) for row in mongo_db.headers.find()]
    for mongo_header in mongo_headers:
        postgres_header = model_postgres_app.Header(**mongo_header.dict())
        postgres_db.add(postgres_header)

    mongo_subscribers = [model_mongo_bot.Subscriber(**row) for row in mongo_db.subscribers.find()]
    for mongo_subscriber in mongo_subscribers:
        postgres_subscriber = model_postgres_bot.Subscriber(
            id=mongo_subscriber.id,
            active=mongo_subscriber.active,
            **mongo_subscriber.parameters.dict()
        )
        postgres_db.add(postgres_subscriber)

    mongo_towns = [model_mongo_app.Town(**row) for row in mongo_db.towns.find()]
    for mongo_town in mongo_towns:
        postgres_town = model_postgres_app.Town(**mongo_town.dict())
        postgres_db.add(postgres_town)
    postgres_db.flush()

    mongo_areas = [model_mongo_app.Area(**row) for row in mongo_db.areas.find()]
    for mongo_area in mongo_areas:
        postgres_area = model_postgres_app.Area(**mongo_area.dict())
        postgres_db.add(postgres_area)

    mongo_ads = [model_mongo_app.Ad(**row) for row in mongo_db.flats.find()]
    for mongo_ad in mongo_ads:
        postgres_ad = model_postgres_app.Ad(
            id=mongo_ad.id,
            created=mongo_ad.created,
            updated=mongo_ad.last_update,
            last_seen=mongo_ad.last_seen,
            removed=mongo_ad.removed,
            last_condition_removed=mongo_ad.last_condition_removed,
            thumbnail_url=mongo_ad.thumbnail_url,
            title=mongo_ad.title,
            lat=mongo_ad.lat,
            lon=mongo_ad.lon,
            attributes=mongo_ad.attributes,
            url=mongo_ad.url,
            photos=mongo_ad.photos,
            map_image=mongo_ad.map_image,
            address_town=mongo_ad.address_town
        )
        postgres_db.add(postgres_ad)

        for mongo_price in mongo_ad.history_price:
            postgres_price = model_postgres_app.Price(ad_id=mongo_ad.id, **mongo_price.dict())
            postgres_db.add(postgres_price)

        mongo_data_ad = mongo_ad.data
        if mongo_data_ad:
            postgres_data_ad = model_postgres_app.DataAd(ad_id=mongo_ad.id, **mongo_data_ad.dict())
            postgres_db.add(postgres_data_ad)

    mongo_telegram_posts = [model_mongo_bot.TelegramIdAd(**row) for row in mongo_db.telegram_posts.find()]
    for mongo_telegram_post in mongo_telegram_posts:
        postgres_telegram_post = model_postgres_bot.TelegramPost(
            ad_id=mongo_telegram_post.id,
            channel_message_id=mongo_telegram_post.telegram_channel_message_id,
            chat_message_id=mongo_telegram_post.telegram_chat_message_id
        )
        postgres_db.add(postgres_telegram_post)

    postgres_db.commit()


def downgrade():
    op.execute(f"DELETE FROM HEADERS")
    op.execute(f"DELETE FROM COOKIES")
    op.execute(f"DELETE FROM SUBSCRIBERS")
    op.execute(f"DELETE FROM TELEGRAM_POSTS")
    op.execute(f"DELETE FROM AREAS")
    op.execute(f"DELETE FROM DATA_ADS")
    op.execute(f"DELETE FROM PRICES")
    op.execute(f"DELETE FROM ADS")
    op.execute(f"DELETE FROM TOWNS")
