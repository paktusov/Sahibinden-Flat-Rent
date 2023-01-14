from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler

from bot.subscription import inline_keyboard_button, CHECK_FURNITURE, end_second_level, NEW_SUBSCRIBE, END


async def get_furniture(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["furniture"] = context.user_data.get("furniture", ["furnished", "unfurnished"])
    callback_data = update.callback_query.data
    if callback_data in ["furnished", "unfurnished"]:
        if callback_data in context.user_data["furniture"]:
            context.user_data["furniture"].remove(callback_data)
        else:
            context.user_data["furniture"].append(callback_data)

    if not context.user_data["furniture"]:
        context.user_data["furniture"] = ["furnished", "unfurnished"]

    data = context.user_data["furniture"]

    reply_keyboard = [
        [
            inline_keyboard_button("С мебелью", "furnished", data),
            inline_keyboard_button("Без мебели", "unfurnished", data),
        ],
        [
            InlineKeyboardButton("Назад", callback_data="_back"),
        ],
    ]
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
