from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from bot.subscription import AREA, CHECK_AREA, END, NEW_SUBSCRIBE, end_second_level
from mongo import db


async def get_town(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    towns = db.towns.find()
    context.user_data["areas"] = context.user_data.get("areas", {})

    reply_keyboard = [[]]
    for town in towns:
        reply_keyboard[-1].append(InlineKeyboardButton(town["name"], callback_data=town["_id"]))
        if not "all_" + town["_id"] in context.user_data["areas"]:
            context.user_data["areas"]["all_" + town["_id"]] = True
    reply_keyboard.append([InlineKeyboardButton("Назад", callback_data="_back")])
    await update.callback_query.answer()
    text = "Выбери город"
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return AREA


async def get_area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    town_id, area, *_ = update.callback_query.data.split("&") + ["", ""]
    areas = {area["name"]: False for area in db.areas.find({"town_id": town_id}).sort("name", 1)}
    if not area:
        context.user_data["areas"].update(areas)
    elif area == "all":
        context.user_data["areas"]["all_" + town_id] = not context.user_data["areas"]["all_" + town_id]
        context.user_data["areas"].update(areas)
    else:
        context.user_data["areas"][area] = not context.user_data["areas"][area]
        context.user_data["areas"]["all_" + town_id] = False

    reply_keyboard = []
    for area in areas.keys():
        if not reply_keyboard or len(reply_keyboard[-1]) == 3:
            reply_keyboard.append([])
        reply_keyboard[-1].append(
            InlineKeyboardButton(
                text=f"{'✔' if context.user_data['areas'][area] else '✖'} {area}",
                callback_data="&".join([town_id, area]),
            )
        )
    reply_keyboard[-1].append(
        InlineKeyboardButton(
            text=f"{'✔' if context.user_data['areas']['all_' + town_id] else '✖'} Любой",
            callback_data="&".join([town_id, "all"]),
        )
    )
    reply_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="towns")])
    await update.callback_query.answer()
    text = "Выбери район"
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return CHECK_AREA


area_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_town, pattern="towns")],
    states={
        AREA: [
            CallbackQueryHandler(get_area, pattern="^[0-9]{1,2}$"),
        ],
        CHECK_AREA: [
            CallbackQueryHandler(get_town, pattern="towns"),
            CallbackQueryHandler(get_area, pattern=".*"),
        ],
    },
    fallbacks=[CallbackQueryHandler(end_second_level, pattern="_back")],
    map_to_parent={
        END: NEW_SUBSCRIBE,
    },
)
