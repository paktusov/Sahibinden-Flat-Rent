from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler


START, NEW_SUBSCRIBE = range(2)
CHECK_FLOOR = 3
CHECK_ROOMS = 4
CHECK_HEATING = 5
AREA, CHECK_AREA = range(6, 8)
CHECK_FURNITURE = 8
END = ConversationHandler.END

back_button = [InlineKeyboardButton("Назад", callback_data="_back")]


def checkbox(check: bool) -> str:
    return f"{'✅' if check else '❌'}️"


def create_inline_keyboard_button_checkbox(text: str, callback_data: str, data: list) -> InlineKeyboardButton:
    return InlineKeyboardButton(f"{checkbox(callback_data in data)} {text}", callback_data=callback_data)


def create_inline_keyboard_button_checkbox_areas(current_areas, name_area, town_id) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        f"{checkbox(current_areas[name_area])} {name_area}", callback_data="&".join([town_id, name_area])
    )


def create_reply_keyboard_checkbox(buttons: dict[str, str], data: list, column: int = 2):
    reply_keyboard = []
    for callback, text in buttons.items():
        if not reply_keyboard or len(reply_keyboard[-1]) == column:
            reply_keyboard.append([])
        reply_keyboard[-1].append(create_inline_keyboard_button_checkbox(text, callback, data))
    return reply_keyboard


def create_reply_keyboard_checkbox_areas(
    areas: dict[str, bool], current_areas: dict[str, bool], town_id: str, column: int = 3
) -> list:
    reply_keyboard = []
    for name_area in areas:
        if not reply_keyboard or len(reply_keyboard[-1]) == column:
            reply_keyboard.append([])
        reply_keyboard[-1].append(create_inline_keyboard_button_checkbox_areas(current_areas, name_area, town_id))
    return reply_keyboard


def change_selection(buttons: dict[str, str], selected: str, data: list, choice_type: str = "multiple") -> list:
    current_data = data.copy()
    if selected in buttons:
        if selected == "all" or choice_type == "single":
            data.clear()
            if selected not in current_data:
                data.append(selected)
        else:
            if "all" in data:
                data.remove("all")
            # pylint: disable=expression-not-assigned
            data.remove(selected) if selected in data else data.append(selected)
    return data


# pylint: disable=unused-variable
def prepare_data(data):
    for key, value in data.items():
        if not data[key]:
            data[key] = ["all"]


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
