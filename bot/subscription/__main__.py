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

from bot.subscription import END, NEW_SUBSCRIBE, START, subscribe
from bot.subscription.area import area_conversation
from bot.subscription.floor import floor_conversation
from bot.subscription.furniture import furniture_conversation
from bot.subscription.heating import heating_conversation
from bot.subscription.price import price_conversation
from bot.subscription.room import rooms_conversation
from config import telegram_config
from storage.connection.postgres import db
from storage.models import Subscriber


logger = logging.getLogger(__name__)


def update_subscriber(active: bool, data: dict):
    logging.info(data)
    current_subscriber = db.query(Subscriber).where(Subscriber.id == data.get("id")).first()
    if not current_subscriber:
        current_subscriber = Subscriber(active=active, **data)
        db.add(current_subscriber)
    else:
        current_subscriber.active = active
        for field, value in data.items():
            setattr(current_subscriber, field, value)
    db.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.sender_chat:
        await context.bot.send_message(
            update.message.sender_chat.id,
            "Для подписки на уведомления, пожалуйста, "
            f"напишите мне в личные сообщения {telegram_config.antalya_bot_username}",
        )
        return ConversationHandler.END
    user_id = update.message.chat.id
    context.user_data["id"] = user_id
    current_user = db.query(Subscriber).where(Subscriber.id == user_id).first()

    fields = {
        "max_price": "Цена",
        "floor": "Этаж",
        "rooms": "Комнаты",
        "heating": "Отопление",
        "areas": "Районы",
        "furniture": "Мебель",
    }
    for field in fields:
        context.user_data[field] = current_user.__dict__[field]

    logging.info(current_user)
    if current_user and current_user.active:
        text = "Ты уже подписан на уведомления. Отредактировать параметры подписки или отписаться?"
        inline_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Редактировать", callback_data="edit"),
                    InlineKeyboardButton("Отписаться", callback_data="cancel"),
                ]
            ]
        )
    else:
        text = "Чтобы начать, нажми 'Продолжить'"
        inline_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Продолжить", callback_data="continue"),
                ]
            ]
        )

    await context.bot.send_message(
        user_id,
        text,
        reply_markup=inline_keyboard,
    )
    return START


async def success_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    update_subscriber(True, context.user_data)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Отлично! Жди уведомлений о новых квартирах")
    return END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not context.user_data.get("id") and not update.message:
        return END
    context.user_data["id"] = context.user_data.get("id") or update.message.from_user.id

    update_subscriber(False, context.user_data)

    await context.bot.send_message(context.user_data["id"], "До свидания! Уведомления отключены")
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
