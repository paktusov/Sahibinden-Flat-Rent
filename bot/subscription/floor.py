from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler

from bot.subscription import inline_keyboard_button, CHECK_FLOOR, end_second_level, NEW_SUBSCRIBE, END


async def get_floor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["floor"] = context.user_data.get("floor", ["all"])
    callback_data = update.callback_query.data
    if callback_data in ["without_basement", "without_first", "without_last"]:
        if "all" in context.user_data["floor"]:
            context.user_data["floor"].remove("all")
        if callback_data in context.user_data["floor"]:
            context.user_data["floor"].remove(callback_data)
        else:
            context.user_data["floor"].append(callback_data)
    elif update.callback_query.data == "all":
        context.user_data["floor"] = ["all"]

    data = context.user_data["floor"]

    reply_keyboard = [
        [
            inline_keyboard_button("Любой", "all", data),
            inline_keyboard_button("Кроме подвала/цоколя", "without_basement", data),
        ],
        [
            inline_keyboard_button("Кроме первого этажа", "without_first", data),
            inline_keyboard_button("Кроме последнего этажа", "without_last", data),
        ],
        [
            InlineKeyboardButton("Назад", callback_data="_back"),
        ],
    ]
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
