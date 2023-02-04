import logging
import uuid
from datetime import datetime

from sqlalchemy import update
from sqlalchemy.orm import selectinload

# from bot.notification import telegram_notify
from storage.__main__ import ads_table
from storage.connection.postgres import db
from storage.models import Ad, Price

from app.models import AdDTO
from app.get_data import get_data_and_photos_ad, get_data_with_cookies, get_map_image

from app.models import DataAd


logger = logging.getLogger(__name__)


def create_dataad_from_data(data: dict) -> DataAd:
    return DataAd(
        region=data.get("loc2"),
        district=data.get("loc3"),
        area=data.get("loc5"),
        creation_date=datetime.strptime(data.get("Ad Date"), "%d %B %Y"),
        gross_area=data.get("m² (Brüt)"),
        net_area=data.get("m² (Net)"),
        room_count=data.get("Oda Sayısı"),
        building_age=data.get("Bina Yaşı"),
        floor=data.get("Bulunduğu Kat"),
        building_floor_count=int(data.get("Kat Sayısı")),
        heating_type=data.get("Isıtma"),
        bathroom_count=data.get("Banyo Sayısı"),
        balcony=bool(data.get("Balkon")),
        furniture=bool(data.get("Eşyalı") == "Yes"),
        using_status=data.get("Kullanım Durumu"),
        dues=data.get("Aidat (TL)"),
        deposit=data.get("Depozito (TL)"),
    )


def create_ad_from_data(data: list[dict], parameters: dict) -> list[Ad]:
    return [Ad(**row, **parameters) for row in data if not (int(row["id"]) < 1000000000 and not row["thumbnailUrl"])]


class PgStorage:
    def __init__(self):
        self.now = datetime.utcnow()

    def commit(self):
        db.commit()

    def find_ads(self, ids: list[str]) -> list[Ad]:
        return db.query(Ad).where(Ad.id.in_(ids)).options(selectinload(Ad.prices)).all()

    def create_price(self, ad: Ad, price: float):
        db.add(Price(ad_id=ad.id, price=price))

    def update_fields(self, ad: Ad, parsed_ad: AdDTO) -> bool:
        ad_changed = False
        logging.info(ad.prices)
        if ad.prices[-1] != parsed_ad.price:
            self.create_price(ad, parsed_ad.price)
            ad_changed = True

        # TODO: добавить нужные поля для отслеживания
        for field in ('title', 'lat', 'lan'):
            if (value := getattr(parsed_ad, field)) != getattr(ad, field):
                setattr(ad, field, value)

        if ad.removed:
            ad.removed = False

        ad_changed = ad_changed or ad in db.dirty

        if ad_changed:
            ad.updated = self.now

        return ad_changed

    def update_last_seen(self, ad_ids: list[str]):
        db.execute(update(Ad).where(Ad.id.in_(ad_ids)).values(last_seen=self.now))

    def create_from_dto(self, ad: AdDTO):
        # TODO: наверно нужны какие-то преобразования еще, например выкинуть поле price
        fields = set(Ad.__dict__)

        db.add(
            Ad(**{k: v for k, v in ad.dict().items() if k in fields})
        )

    def get_missed_ads(self, **parameters):
        # TODO: хз какой тут синтаксис надо
        return db.query(Ad).where({"last_seen": {"$lt": self.now}, "removed": False, **parameters})


async def processing_data(parameters: dict) -> None:
    pg_storage = PgStorage()

    parsed_ads = {ad.id: ad for ad in get_data_with_cookies(parameters)}
    if not parsed_ads:
        logger.warning("Can't parse ads from sahibinden.com")
        return

    # ищем старые объявления
    existed_ads = {ad.id: ad for ad in pg_storage.find_ads(list(parsed_ads))}

    # актуализируем информациюв старых объявлениях, убираем removed, обновляем посты в телеге
    for ad_id, ad in existed_ads.items():
        is_dirty = pg_storage.update_fields(ad, existed_ads[ad_id])

        # обновляем пост телеги при измененниях
        # if is_dirty:
        #     await telegram_notify(ad)

    # обновляем last_seen для найденых объявлений
    pg_storage.update_last_seen(list(existed_ads))

    # добавляем новые
    for ad_id in parsed_ads:
        pg_storage.create_from_dto(parsed_ads[ad_id])
        # await telegram_notify(ad)

    # коммитим все изменения
    pg_storage.commit()

    # TODO: доделать
    # missed_ad = pg_storage.get_missed(**parameters)
    # for ad in missed_ad:
    #     ad.remove()
        # flats_table.find_oneF_and_replace(ad.id, ad.dict(by_alias=True))
        # await telegram_notify(ad)
