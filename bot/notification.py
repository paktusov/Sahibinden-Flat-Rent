import logging

from telegram import InputMediaPhoto
from telegram.error import TelegramError

from bot.bot import application
from bot.check_subscription import subscription_validation
from config import telegram_config
from storage.connection.postgres import postgres_db
from storage.models.postgres.app import Ad, Area
from storage.models.postgres.bot import Subscriber, TelegramPost


chat_id = telegram_config.id_antalya_chat
channel_id = telegram_config.id_antalya_channel

logger = logging.getLogger(__name__)

closed_areas = [area.name for area in postgres_db.query(Area).where(Area.is_closed).all()]
connection_parameters = {"connect_timeout": 20, "read_timeout": 20}


def format_price(price: float) -> str:
    return f"{price:,.0f}".replace(",", " ")


def make_caption(ad: Ad, status: str = "new") -> str:
    first_price = format_price(ad.first_price)
    last_price = format_price(ad.last_price)
    date = ad.last_price_update.strftime("%d.%m.%Y")
    hiperlink = f'<a href="{ad.short_url}">{ad.title}</a>\n'

    if status == "new":
        price = f"{last_price} TL\n"
    elif status == "update":
        price = f"<s>{first_price} TL</s> {last_price} TL on {date}\n"
    else:
        price = f"<s>{first_price} TL</s> Ad removed on {date}\n"
    caption = hiperlink + price

    area = ad.area
    if area in closed_areas:
        area += "⛔️"
    caption += f"#{ad.district} / #{area}\n"
    caption += f"{ad.room_count}\n"
    caption += f"{ad.net_area} ({ad.gross_area}) m²\n"
    caption += f"{ad.floor}/{ad.building_floor_count} floor\n"
    caption += f"{ad.building_age} y.o\n"
    caption += f"{ad.heating_type}\n"
    caption += "Furniture" if ad.furniture else "No furniture"

    return caption


async def send_comment_for_ad_to_telegram(ad: Ad) -> None:
    telegram_post = postgres_db.query(TelegramPost).where(TelegramPost.id == ad.id).first()
    if not telegram_post:
        logging.warning("Telegram post not found for ad %s", ad.id)
        return
    telegram_chat_message_id = telegram_post.chat_message_id
    new_price = format_price(ad.last_price)
    price_diff = ad.last_price - ad.previous_price
    formatted_price_diff = format_price(price_diff)
    icon = "📉 " if price_diff < 0 else "📈 +"
    comment = f"{icon}{formatted_price_diff} TL = {new_price} TL"
    try:
        await application.bot.send_message(
            chat_id=chat_id,
            text=comment,
            reply_to_message_id=telegram_chat_message_id,
            parse_mode="HTML",
            **connection_parameters,
        )
        logger.info("Comment ad %s to telegram", ad.id)
    except TelegramError as e:
        logger.error("Error while sending comment for ad %s to telegram: %s", ad.id, e)


async def edit_ad_in_telegram(ad: Ad, status: str) -> None:
    telegram_post = postgres_db.query(TelegramPost).where(TelegramPost.id == ad.id).first()
    if not telegram_post:
        logging.warning("Telegram post not found for ad %s", ad.id)
        return
    telegram_channel_message_id = telegram_post.channel_message_id
    caption = make_caption(ad, status)
    try:
        await application.bot.edit_message_caption(
            chat_id=channel_id,
            message_id=telegram_channel_message_id,
            parse_mode="HTML",
            caption=caption,
            **connection_parameters,
        )
        logger.info("Edit ad %s to telegram", ad.id)
    except TelegramError as e:
        logger.error("Error while editing ad %s in telegram: %s", ad.id, e)


async def send_ad_to_telegram(ad: Ad) -> None:
    media = [InputMediaPhoto(media=ad.map_image, caption=make_caption(ad), parse_mode="HTML")]
    for photo in ad.photos:
        media.append(InputMediaPhoto(media=photo))
    try:
        await application.bot.send_media_group(chat_id=channel_id, media=media, **connection_parameters)
        logger.info("Sending ad %s to telegram", ad.id)
        # pylint: disable=singleton-comparison
        subscribers = postgres_db.query(Subscriber).where(Subscriber.active == True).all()
        for subscriber in subscribers:
            if not subscription_validation(ad, subscriber):
                continue
            await application.bot.send_media_group(chat_id=subscriber.id, media=media, **connection_parameters)
            logger.info("Send message %s to subscriber %s", ad.id, subscriber.id)
    except TelegramError as e:
        logger.error("Error while sending ad %s to telegram: %s", ad.id, e)


async def telegram_notify(ad: Ad) -> None:
    if ad.removed:
        await edit_ad_in_telegram(ad, "remove")
    elif ad.last_seen == ad.created:
        await send_ad_to_telegram(ad)
    elif ad.last_seen == ad.updated:
        await send_comment_for_ad_to_telegram(ad)
        await edit_ad_in_telegram(ad, "update")
    elif ad.last_condition_removed:
        if len(ad.prices) == 1:
            await edit_ad_in_telegram(ad, "new")
        else:
            await edit_ad_in_telegram(ad, "update")
