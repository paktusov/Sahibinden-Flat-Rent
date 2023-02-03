import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import selectinload

from bot.notification import telegram_notify
from storage.__main__ import ads_table
from storage.connection.postgres import db
from storage.models import Ad, DataAd, Price

from app.get_data import get_data_and_photos_ad, get_data_with_cookies, get_map_image

# from app.models import Ad, DataAd


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


def create_ad_and_price_from_data(data: list[dict], parameters: dict) -> list[Ad]:
    now_time = datetime.utcnow()
    ads = []
    for row in data:
        if int(row["id"]) < 1000000000 and not row["thumbnailUrl"]:
            continue
        ads.append(Ad(**row, **{"last_seen": now_time, "created": now_time, }, **parameters, ))
        # if Price.query.filter(Price.ad_id == row.get["id"]).order_by(Price.created.desc()).first().price !=
        # price = Price(id=uuid.uuid4().int & (1 << 64) - 1, ad_id=row.get("id"), price=row.get("price"))

        # db.add(price)
    # db.commit()
    return ads


async def processing_data(parameters: dict) -> None:
    now_time = datetime.utcnow()
    data = get_data_with_cookies(parameters)
    if not data:
        logger.warning("Can't parse ads from sahibinden.com")
        return
    parsed_ads = create_ad_and_price_from_data(data, parameters)

    ids = [ad.id for ad in parsed_ads]

    existed_ads = {}
    for ad in db.query(Ad).where(Ad.id.in_(ids)).options(selectinload(Ad.prices)).all():
        existed_ads[ad["_id"]] = Ad(**ad)

    for ad in parsed_ads:
        if ad.id in existed_ads:
            existed_ads[ad.id].update_price(ad)
            if existed_ads[ad.id].removed:
                existed_ads[ad.id].last_condition_removed = True
        else:
            db.add(ad)
            dataad, photos = get_data_and_photos_ad(ad.full_url)
            if not photos:
                logger.error("Can't parse ad photos from %s", ad.id)
            ad.photos = photos

            map_image = get_map_image(ad.lat, ad.lon)
            if not map_image:
                logger.error("Can't parse ad map image from %s", ad.id)
            ad.map_image = map_image

            if dataad:
                ad.data = create_dataad_from_data(dataad)
            else:
                logger.error("Can't parse ad data from %s", ad.id)

        flats_table.find_one_by_id_and_replace(ad.id, ad.dict(by_alias=True))

        if ad.is_dirty():
            ad.save()
            await telegram_notify(ad)


    db.query(Ad).where(id__in=existed_ads).update(last_seen=now_time, removed=False)

    missed_ad = [
        Ad(**ad) for ad in flats_table.find_many({"last_seen": {"$lt": now_time}, "removed": False, **parameters})
    ]

    for ad in missed_ad:
        ad.remove()
        flats_table.find_oneF_and_replace(ad.id, ad.dict(by_alias=True))
        await telegram_notify(ad)
