import logging
from warnings import filterwarnings

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
from telegram.warnings import PTBUserWarning

from bot.models import Subscriber, SubscriberParameters
from bot.subscription.area import area_conversation
from bot.subscription.floor import floor_conversation
from bot.subscription.furniture import furniture_conversation
from bot.subscription.heating import heating_conversation
from bot.subscription.price import price_conversation
from bot.subscription import START, NEW_SUBSCRIBE, END, new_subscribe
from bot.subscription.room import rooms_conversation
from config import telegram_config
from mongo import db


logger = logging.getLogger(__name__)

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.sender_chat:
        await context.bot.send_message(
            update.message.sender_chat.id,
            "Для подписки на уведомления, пожалуйста,"
            f"напишите мне в личные сообщения {telegram_config.antalya_bot_username}",
        )
        return ConversationHandler.END
    user_id = update.message.chat.id
    context.user_data["user_id"] = user_id
    if db.subscribers.find_one({"_id": user_id, "active": True}):
        await context.bot.send_message(
            user_id,
            "Ты уже подписан на уведомления. Чтобы отписаться, напиши /cancel",
        )
        return ConversationHandler.END

    reply_keyboard = [
        [
            InlineKeyboardButton("Продолжить", callback_data="continue"),
        ]
    ]
    await context.bot.send_message(
        user_id,
        "Привет, ищешь квартиру в Антилии?"
        "Я могу отправлять тебе уведомления о новых квартирах по твоим параметрам поиска.",
    )
    await context.bot.send_message(
        user_id,
        "Чтобы начать, нажми 'Продолжить'",
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return START


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = context.user_data["user_id"]
    parameters = SubscriberParameters(**context.user_data)
    subscriber = Subscriber(
        _id=user_id,
        parameters=parameters,
        active=True,
    )
    db.subscribers.find_one_and_replace({"_id": user_id}, subscriber.dict(by_alias=True), upsert=True)
    await update.callback_query.answer()
    await context.bot.send_message(user_id, "Отлично! Жди уведомлений о новых квартирах")
    return END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = context.user_data.get("user_id", update.message.from_user.id)
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
                    CallbackQueryHandler(new_subscribe, pattern="continue"),
                    MessageHandler(filters.TEXT, start),
                ],
                NEW_SUBSCRIBE: [
                    price_conversation,
                    floor_conversation,
                    rooms_conversation,
                    heating_conversation,
                    area_conversation,
                    furniture_conversation,
                    CallbackQueryHandler(subscribe, pattern="subscribe"),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            per_chat=False,
            allow_reentry=True,
        )
    )
