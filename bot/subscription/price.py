from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, ContextTypes

from bot.subscription import inline_keyboard_button, end_second_level, NEW_SUBSCRIBE, END

CHECK_PRICE = 2


async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["max_price"] = context.user_data.get("max_price", ["30000"])
    callback_data = update.callback_query.data
    prices = ["5000", "7500", "10000", "12500", "15000", "20000", "25000"]
    if callback_data != "price":
        context.user_data["max_price"] = [callback_data]

    data = context.user_data["max_price"]

    reply_keyboard = []
    for price in prices:
        if not reply_keyboard or len(reply_keyboard[-1]) == 2:
            reply_keyboard.append([])
        reply_keyboard[-1].append(inline_keyboard_button(price, price, data))
    reply_keyboard[-1].append(inline_keyboard_button("Любая", "30000", data))
    reply_keyboard.append([InlineKeyboardButton("Назад", callback_data="_back")])
    text = "Какую максимальную сумму TL ты готов потратить на аренду в месяц?"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return CHECK_PRICE


price_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_price, pattern="price")],
    states={
        CHECK_PRICE: [
            CallbackQueryHandler(get_price, pattern="^[0-9]{1,6}$"),
        ],
    },
    fallbacks=[CallbackQueryHandler(end_second_level, pattern="_back")],
    map_to_parent={
        END: NEW_SUBSCRIBE,
    },
)
