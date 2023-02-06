from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from bot.subscription import (
    CHECK_ROOMS,
    END,
    NEW_SUBSCRIBE,
    back_button,
    change_selection,
    create_reply_keyboard_checkbox,
    end_second_level,
)


async def get_room(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    options = {
        "0": "Студия",
        "1": "Одна",
        "2": "Две",
        "3": "Три",
        "4": "Четыре и более",
        "all": "Любое количество",
    }
    current_rooms = context.user_data.get("rooms")
    if not current_rooms:
        current_rooms = ["all"]
    selected = update.callback_query.data

    context.user_data["rooms"] = change_selection(options, selected, current_rooms)

    reply_keyboard = create_reply_keyboard_checkbox(options, context.user_data["rooms"])
    reply_keyboard.append(back_button)

    await update.callback_query.answer()
    text = "Какое количество комнат тебе нужно?"
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return CHECK_ROOMS


rooms_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_room, pattern="rooms")],
    states={
        CHECK_ROOMS: [
            CallbackQueryHandler(get_room, pattern="^[^_].*"),
        ],
    },
    fallbacks=[CallbackQueryHandler(end_second_level, pattern="_back")],
    map_to_parent={
        END: NEW_SUBSCRIBE,
    },
)
