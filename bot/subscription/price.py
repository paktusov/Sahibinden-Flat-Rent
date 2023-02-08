from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from bot.subscription import (
    END,
    NEW_SUBSCRIBE,
    back_button,
    change_selection,
    create_reply_keyboard_checkbox,
    end_second_level,
)


CHECK_PRICE = 2


async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    options = {
        "5000": "5000",
        "7500": "7500",
        "10000": "10000",
        "12500": "12500",
        "15000": "15000",
        "20000": "20000",
        "25000": "25000",
        "30000": "Любая",
    }
    current_max_price = context.user_data.get("max_price", ["30000"])
    selected = update.callback_query.data

    context.user_data["max_price"] = change_selection(options, selected, current_max_price, "single")

    reply_keyboard = create_reply_keyboard_checkbox(options, context.user_data["max_price"])
    reply_keyboard.append(back_button)

    await update.callback_query.answer()
    text = "Какую максимальную сумму TL ты готов потратить на аренду в месяц?"
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return CHECK_PRICE


price_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_price, pattern="max_price")],
    states={
        CHECK_PRICE: [
            CallbackQueryHandler(get_price, pattern="^[0-9]{1,6}$"),
            CallbackQueryHandler(get_price, pattern="all"),
        ],
    },
    fallbacks=[CallbackQueryHandler(end_second_level, pattern="_back")],
    map_to_parent={
        END: NEW_SUBSCRIBE,
    },
)
