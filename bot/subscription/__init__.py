from telegram.ext import ContextTypes, ConversationHandler

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update


START, NEW_SUBSCRIBE = range(2)
CHECK_FLOOR = 3
CHECK_ROOMS = 4
CHECK_HEATING = 5
AREA, CHECK_AREA = range(6, 8)
CHECK_FURNITURE = 8
END = ConversationHandler.END

back_button = [InlineKeyboardButton("Назад", callback_data="_back")]


def create_inline_keyboard_button_markup(text: str, callback_data: str, data: list) -> InlineKeyboardButton:
    def markup(d):
        return f"{'✔' if d in data else '✖'}️"

    return InlineKeyboardButton(f"{markup(callback_data)} {text}", callback_data=callback_data)


def create_reply_keyboard(buttons: dict[str, str], data: list, column: int = 2):
    reply_keyboard = []
    for callback, text in buttons.items():
        if not reply_keyboard or len(reply_keyboard[-1]) == column:
            reply_keyboard.append([])
        reply_keyboard[-1].append(create_inline_keyboard_button_markup(text, callback, data))

    return reply_keyboard


def change_selection(buttons: dict[str, str], selected: str, data: list, choice_type: str = "multiple") -> list:
    if selected == "all":
        data.clear()
    if selected in buttons:
        if "all" in data:
            data.remove("all")
        if choice_type == "multiple":
            # pylint: disable=expression-not-assigned
            data.remove(selected) if selected in data else data.append(selected)
        elif choice_type == "single":
            data.clear()
            data.append(selected)
    return ["all"] if not data else data


# pylint: disable=unused-argument
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    await subscribe(update, context)
    return END
