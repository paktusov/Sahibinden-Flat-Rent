import logging
from datetime import datetime

from bot.notification import telegram_notify
from storage.connection.postgres import db
from storage.models import Ad, Price

from app.models import AdDTO
from app.get_data import get_data_and_photos_ad, get_data_with_cookies, get_map_image


logger = logging.getLogger(__name__)


def update_ad_from_data(ad: Ad, data: dict) -> None:
    ad.region = data.get("loc2")
    ad.district = data.get("loc3")
    ad.area = data.get("loc5")
    ad.creation_date = datetime.strptime(data.get("Ad Date"), "%d %B %Y")
    ad.gross_area = data.get("m² (Brüt)")
    ad.net_area = data.get("m² (Net)")
    ad.room_count = data.get("Oda Sayısı")
    ad.building_age = data.get("Bina Yaşı")
    ad.floor = data.get("Bulunduğu Kat")
    ad.building_floor_count = int(data.get("Kat Sayısı"))
    ad.heating_type = data.get("Isıtma")
    ad.bathroom_count = data.get("Banyo Sayısı")
    ad.balcony = bool(data.get("Balkon"))
    ad.furniture = bool(data.get("Eşyalı") == "Yes")
    ad.using_status = data.get("Kullanım Durumu")
    ad.dues = data.get("Aidat (TL)")
    ad.deposit = data.get("Depozito (TL)")


def create_price(ad: Ad, parsed_ad: AdDTO):
    db.add(Price(ad_id=ad.id, price=parsed_ad.price, created=parsed_ad.created, updated=parsed_ad.created))


def update_price(ad: Ad, parsed_ad: AdDTO) -> bool:
    ad.last_seen = parsed_ad.last_seen
    if ad.prices[-1].price != parsed_ad.price:
        create_price(ad, parsed_ad)

    if ad.removed:
        ad.last_condition_removed = True
        ad.removed = False


def create_ad_from_dto(parsed_ad: AdDTO):
    fields = set(Ad.__dict__)
    ad = Ad(**{k: v for k, v in parsed_ad.dict().items() if k in fields})
    db.add(ad)
    create_price(ad, parsed_ad)
    return ad


def get_missed_ads(start_processing, parameters):
    query = db.query(Ad).where(Ad.last_seen >= start_processing, Ad.removed is False)
    for field, value in parameters.items():
        query = query.where(Ad.__dict__[field] == value)
    return query.all()


async def processing_data(parameters: dict) -> None:
    start_processing = datetime.utcnow()

    parsed_ads = {ad.id: ad for ad in get_data_with_cookies(parameters)}
    if not parsed_ads:
        logger.warning("Can't parse ads from sahibinden.com")
        return
    existed_ads = {ad.id: ad for ad in db.query(Ad).where(Ad.id.in_(list(parsed_ads))).all()}

    for ad_id, ad in parsed_ads.items():
        if ad_id in existed_ads:
            current_ad = existed_ads[ad_id]
            update_price(current_ad, ad)
        else:
            current_ad = create_ad_from_dto(ad)

            dataad, photos = get_data_and_photos_ad(ad.full_url)
            if dataad:
                update_ad_from_data(current_ad, dataad)
            else:
                logger.error("Can't parse ad data from %s", ad.id)
            if not photos:
                logger.error("Can't parse ad photos from %s", ad.id)
            current_ad.photos = photos

            map_image = get_map_image(ad.lat, ad.lon)
            if not map_image:
                logger.error("Can't parse ad map image from %s", ad.id)
            current_ad.map_image = map_image

        db.flush()
        await telegram_notify(current_ad)
    db.commit()

    missed_ads = get_missed_ads(start_processing, parameters)
    for ad in missed_ads:
        ad.remove()
        await telegram_notify(ad)
    db.commit()
