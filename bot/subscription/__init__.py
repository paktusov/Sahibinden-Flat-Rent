from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler


START, NEW_SUBSCRIBE = range(2)
CHECK_FLOOR = 3
CHECK_ROOMS = 4
CHECK_HEATING = 5
AREA, CHECK_AREA = range(6, 8)
CHECK_FURNITURE = 8
END = ConversationHandler.END


def inline_keyboard_button(text: str, callback_data: str, data: list) -> InlineKeyboardButton:
    def markup(d):
        return f"{'✔' if d in data else '✖'}️"

    return InlineKeyboardButton(f"{markup(callback_data)} {text}", callback_data=callback_data)


# pylint: disable=unused-argument
async def new_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [
        [
            InlineKeyboardButton("Цена", callback_data="price"),
            InlineKeyboardButton("Этаж", callback_data="floor"),
        ],
        [
            InlineKeyboardButton("Комнаты", callback_data="rooms"),
            InlineKeyboardButton("Отопление", callback_data="heating"),
        ],
        [
            InlineKeyboardButton("Районы", callback_data="towns"),
            InlineKeyboardButton("Мебель", callback_data="furniture"),
        ],
        [
            InlineKeyboardButton("Подписаться", callback_data="subscribe"),
        ],
    ]
    text = "Выбери требуемые параметры поиска и нажми 'Подписаться'"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return NEW_SUBSCRIBE


async def end_second_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await new_subscribe(update, context)
    return END
