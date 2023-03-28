from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from bot.subscription import (
    CHECK_FURNITURE,
    END,
    NEW_SUBSCRIBE,
    back_button,
    change_selection,
    create_reply_keyboard_checkbox,
    end_second_level,
)


async def get_furniture(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    options = {
        "furnished": "С мебелью",
        "unfurnished": "Без мебели",
        "all": "Не имеет значения",
    }
    current_furniture = context.user_data.get("furniture", ["all"])
    selected = update.callback_query.data

    context.user_data["furniture"] = change_selection(buttons=options, selected=selected, data=current_furniture)

    reply_keyboard = create_reply_keyboard_checkbox(buttons=options, data=context.user_data["furniture"])
    reply_keyboard.append(back_button)

    await update.callback_query.answer()
    text = "Нужна ли мебель?"
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return CHECK_FURNITURE


furniture_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_furniture, pattern="furniture")],
    states={
        CHECK_FURNITURE: [
            CallbackQueryHandler(get_furniture, pattern="^[^_].*"),
        ],
    },
    fallbacks=[CallbackQueryHandler(end_second_level, pattern="_back")],
    map_to_parent={
        END: NEW_SUBSCRIBE,
    },
)
