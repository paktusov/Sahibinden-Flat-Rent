"""data

Revision ID: 50e8142ee506
Revises: b9d4fb17eb8d
Create Date: 2023-03-27 15:00:15.661562

"""
import sqlalchemy as sa
from alembic import op

import storage.models.mongo.app as model_mongo_app
import storage.models.mongo.bot as model_mongo_bot
import storage.models.postgres.app as model_postgres_app
import storage.models.postgres.bot as model_postgres_bot
from storage.connection.mongo import mongo_db
from storage.connection.postgres import postgres_db


# revision identifiers, used by Alembic.
revision = "50e8142ee506"
down_revision = "b9d4fb17eb8d"
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
            id=mongo_subscriber.id, active=mongo_subscriber.active, **mongo_subscriber.parameters.dict()
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
        if not mongo_ad.data:
            continue
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
            address_town=mongo_ad.address_town,
            **mongo_ad.data.dict(),
        )
        postgres_db.add(postgres_ad)

        for mongo_price in mongo_ad.history_price:
            postgres_price = model_postgres_app.Price(ad_id=mongo_ad.id, **mongo_price.dict())
            postgres_db.add(postgres_price)

    mongo_telegram_posts = [model_mongo_bot.TelegramIdAd(**row) for row in mongo_db.telegram_posts.find()]
    for mongo_telegram_post in mongo_telegram_posts:
        postgres_telegram_post = model_postgres_bot.TelegramPost(
            ad_id=mongo_telegram_post.id,
            channel_message_id=mongo_telegram_post.telegram_channel_message_id,
            chat_message_id=mongo_telegram_post.telegram_chat_message_id,
        )
        postgres_db.add(postgres_telegram_post)

    postgres_db.commit()


def downgrade():
    op.execute(f"TRUNCATE TABLE HEADERS")
    op.execute(f"TRUNCATE TABLE COOKIES")
    op.execute(f"TRUNCATE TABLE SUBSCRIBERS")
    op.execute(f"TRUNCATE TABLE TELEGRAM_POSTS")
    op.execute(f"TRUNCATE TABLE AREAS")
    op.execute(f"TRUNCATE TABLE PRICES")
    op.execute(f"TRUNCATE TABLE ADS")
    op.execute(f"TRUNCATE TABLE TOWNS")
