from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from telegram import Update, InlineKeyboardMarkup
from bot.subscription import (
    CHECK_HEATING,
    END,
    NEW_SUBSCRIBE,
    back_button,
    change_selection,
    create_reply_keyboard_checkbox,
    end_second_level,
)


async def get_heating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    options = {
        "gas": "Газовое",
        "electricity": "Электрическое",
        "central": "Центральное",
        "underfloor": "Теплый пол",
        "ac": "Кондиционер",
        "all": "Любое",
    }
    current_heating = context.user_data["heating"]
    selected = update.callback_query.data

    context.user_data["heating"] = change_selection(options, selected, current_heating)

    reply_keyboard = create_reply_keyboard_checkbox(options, context.user_data["heating"])
    reply_keyboard.append(back_button)

    await update.callback_query.answer()
    text = "Выбери тип отопления"
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return CHECK_HEATING


heating_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_heating, pattern="heating")],
    states={
        CHECK_HEATING: [
            CallbackQueryHandler(get_heating, pattern="^[^_].*"),
        ],
    },
    fallbacks=[CallbackQueryHandler(end_second_level, pattern="_back")],
    map_to_parent={
        END: NEW_SUBSCRIBE,
    },
)
