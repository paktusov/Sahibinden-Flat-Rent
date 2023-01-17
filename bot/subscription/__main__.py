import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.models import Subscriber, SubscriberParameters
from bot.subscription import END, NEW_SUBSCRIBE, START, subscribe, prepare_data
from bot.subscription.area import area_conversation
from bot.subscription.floor import floor_conversation
from bot.subscription.furniture import furniture_conversation
from bot.subscription.heating import heating_conversation
from bot.subscription.price import price_conversation
from bot.subscription.room import rooms_conversation
from config import telegram_config
from mongo import db


logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.sender_chat:
        await context.bot.send_message(
            update.message.sender_chat.id,
            "Для подписки на уведомления, пожалуйста, "
            f"напишите мне в личные сообщения {telegram_config.antalya_bot_username}",
        )
        return ConversationHandler.END
    user_id = update.message.chat.id
    context.user_data["_id"] = user_id
    current_user = db.subscribers.find_one({"_id": user_id})

    if current_user and current_user["active"]:
        context.user_data.update(current_user["parameters"])
        text = "Ты уже подписан на уведомления. Отредактировать параметры подписки или отписаться?"
        inline_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("Редактировать", callback_data="edit"),
            InlineKeyboardButton("Отписаться", callback_data="cancel"),
        ]])
    else:
        context.user_data.update(SubscriberParameters().dict())
        text = "Чтобы начать, нажми 'Продолжить'"
        inline_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Продолжить", callback_data="continue"), ]])

    await context.bot.send_message(
        user_id,
        text,
        reply_markup=inline_keyboard,
    )
    return START


async def success_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = context.user_data["_id"]
    prepare_data(context.user_data)
    parameters = SubscriberParameters(**context.user_data)
    subscriber = Subscriber(
        _id=user_id,
        parameters=parameters,
        active=True,
    )
    db.subscribers.find_one_and_replace({"_id": user_id}, subscriber.dict(by_alias=True), upsert=True)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Отлично! Жди уведомлений о новых квартирах")
    return END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not context.user_data.get("_id") and not update.message:
        return END
    user_id = context.user_data.get("_id") or update.message.from_user.id
    db.subscribers.find_one_and_update({"_id": user_id}, {"$set": {"active": False}})
    await context.bot.send_message(user_id, "До свидания! Уведомления отключены")
    return END


def setup_cancel(application: Application) -> None:
    application.add_handler(CommandHandler("cancel", cancel))


def setup_conversation(application: Application) -> None:
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                START: [
                    CallbackQueryHandler(cancel, pattern="cancel"),
                    CallbackQueryHandler(subscribe, pattern="^.*"),
                    MessageHandler(filters.TEXT, start),
                ],
                NEW_SUBSCRIBE: [
                    price_conversation,
                    floor_conversation,
                    rooms_conversation,
                    heating_conversation,
                    area_conversation,
                    furniture_conversation,
                    CallbackQueryHandler(success_subscribe, pattern="subscribe"),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            per_chat=False,
            allow_reentry=True,
        )
    )
