from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler

from bot.subscription import inline_keyboard_button, CHECK_ROOMS, end_second_level, NEW_SUBSCRIBE, END


async def get_room(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["rooms"] = context.user_data.get("rooms", ["all"])
    callback_data = update.callback_query.data
    if callback_data in ["0", "1", "2", "3", "4"]:
        if "all" in context.user_data["rooms"]:
            context.user_data["rooms"].remove("all")
        if callback_data in context.user_data["rooms"]:
            context.user_data["rooms"].remove(callback_data)
        else:
            context.user_data["rooms"].append(callback_data)
    elif update.callback_query.data == "all":
        context.userCHECK_PRICE_data["rooms"] = ["all"]

    data = context.user_data["rooms"]

    reply_keyboard = [
        [
            inline_keyboard_button("Cтудия", "0", data),
            inline_keyboard_button("Одна", "1", data),
        ],
        [
            inline_keyboard_button("Две", "2", data),
            inline_keyboard_button("Три", "3", data),
        ],
        [
            inline_keyboard_button("Четыре", "4", data),
            inline_keyboard_button("Любое количество", "all", data),
        ],
        [
            InlineKeyboardButton("Назад", callback_data="_back"),
        ],
    ]
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
