from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from bot.subscription import (
    CHECK_FLOOR,
    END,
    NEW_SUBSCRIBE,
    back_button,
    change_selection,
    create_reply_keyboard_checkbox,
    end_second_level,
)


async def get_floor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    options = {
        "all": "Любой",
        "without_basement": "Кроме подвала/цоколя",
        "without_first": "Кроме первого этажа",
        "without_last": "Кроме последнего этажа",
    }
    current_floor = context.user_data.get("floor", ["all"])
    selected = update.callback_query.data

    context.user_data["floor"] = change_selection(options, selected, current_floor)
    reply_keyboard = create_reply_keyboard_checkbox(options, context.user_data["floor"])
    reply_keyboard.append(back_button)

    await update.callback_query.answer()
    text = "Выбери этажи, которые тебе подходят"
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return CHECK_FLOOR


floor_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_floor, pattern="floor")],
    states={
        CHECK_FLOOR: [
            CallbackQueryHandler(get_floor, pattern="^[^_].*"),
        ],
    },
    fallbacks=[CallbackQueryHandler(end_second_level, pattern="_back")],
    map_to_parent={
        END: NEW_SUBSCRIBE,
    },
)
