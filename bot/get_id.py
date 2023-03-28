import logging

from telegram import Update
from telegram.ext import Application, CallbackContext, MessageHandler, filters

from config import telegram_config
from storage.connection.postgres import postgres_db
from storage.models.postgres.bot import TelegramPost


chat_id = telegram_config.id_antalya_chat
channel_id = telegram_config.id_antalya_channel

logger = logging.getLogger(__name__)


def update_post_information(ad_id, telegram_channel_message_id, telegram_chat_message_id):
    current_post = postgres_db.query(TelegramPost).where(TelegramPost.ad_id == ad_id).first()
    if current_post:
        current_post.channel_message_id = telegram_channel_message_id
        current_post.chat_message_id = telegram_chat_message_id
    else:
        post = TelegramPost(
            ad_id=ad_id,
            channel_message_id=telegram_channel_message_id,
            chat_message_id=telegram_chat_message_id,
        )

        postgres_db.add(post)
    postgres_db.commit()


# pylint: disable=unused-argument
async def get_telegram_message_id(update: Update, context: CallbackContext) -> None:
    telegram_chat_message_id = update.message.message_id
    telegram_channel_message_id = update.message.forward_from_message_id
    url = update.message.caption_entities[0].url
    ad_id = url.replace("https://www.sahibinden.com/", "")
    update_post_information(ad_id, telegram_channel_message_id, telegram_chat_message_id)
    logger.info("Telegram post %s saved", ad_id)


def setup_get_id(application: Application) -> None:
    application.add_handler(
        MessageHandler(
            filters.PHOTO
            & filters.CaptionEntity("text_link")
            & filters.ForwardedFrom(chat_id=int(channel_id))
            & filters.UpdateType.MESSAGE,
            get_telegram_message_id,
        )
    )
