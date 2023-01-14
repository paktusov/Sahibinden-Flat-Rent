from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler

from bot.subscription import inline_keyboard_button, CHECK_HEATING, end_second_level, NEW_SUBSCRIBE, END


async def get_heating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["heating"] = context.user_data.get("heating", ["all"])
    callback_data = update.callback_query.data
    if callback_data in ["gas", "electricity", "underfloor", "central", "ac"]:
        if "all" in context.user_data["heating"]:
            context.user_data["heating"].remove("all")
        if callback_data not in context.user_data["heating"]:
            context.user_data["heating"].append(callback_data)
        else:
            context.user_data["heating"].remove(callback_data)
    elif callback_data == "all":
        context.user_data["heating"] = ["all"]

    data = context.user_data["heating"]

    reply_keyboard = [
        [
            inline_keyboard_button("Газовое", "gas", data),
            inline_keyboard_button("Электрическое", "electricity", data),
        ],
        [
            inline_keyboard_button("Теплый пол", "underfloor", data),
            inline_keyboard_button("Центральное", "central", data),
        ],
        [
            inline_keyboard_button("Кондиционер", "ac", data),
            inline_keyboard_button("Любое", "all", data),
        ],
        [
            InlineKeyboardButton("Назад", callback_data="_back"),
        ],
    ]
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
