from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from bot.subscription import (
    AREA,
    CHECK_AREA,
    END,
    NEW_SUBSCRIBE,
    back_button,
    checkbox,
    create_reply_keyboard_checkbox_areas,
    end_second_level,
)
from storage.connection.postgres import postgres_db
from storage.models.postgres.app import Area, Town


DEFAULT_AREAS = {"83": True, "84": True, "85": True}


# pylint: disable=unused-argument
async def get_town(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    towns = postgres_db.query(Town).all()
    reply_keyboard = [[]]
    for town in towns:
        reply_keyboard[-1].append(InlineKeyboardButton(town.name, callback_data=town.id))
    reply_keyboard.append(back_button)

    await update.callback_query.answer()
    text = "Выбери город"
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return AREA


async def get_area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_town_id, selected_area, *_ = update.callback_query.data.split("&") + ["", ""]
    areas = {
        area.name: False
        for area in postgres_db.query(Area).where(Area.town_id == selected_town_id).order_by(Area.name).all()
    }
    if "areas" not in context.user_data or not context.user_data["areas"]:
        context.user_data["areas"] = DEFAULT_AREAS
    current_areas = context.user_data["areas"]

    if not selected_area:
        for area in areas:
            if area in current_areas:
                continue
            current_areas[area] = areas[area]
    elif selected_area == "all":
        current_areas[selected_town_id] = not current_areas[selected_town_id]
        current_areas.update(areas)
    else:
        current_areas[selected_area] = not current_areas[selected_area]
        current_areas[selected_town_id] = False
    reply_keyboard = create_reply_keyboard_checkbox_areas(areas, current_areas, selected_town_id)
    reply_keyboard[-1].append(
        InlineKeyboardButton(
            text=f"{checkbox(current_areas[selected_town_id])} Любой",
            callback_data="&".join([selected_town_id, "all"]),
        )
    )
    reply_keyboard.append([InlineKeyboardButton("Назад", callback_data="areas")])

    await update.callback_query.answer()
    text = "Выбери район"
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )
    return CHECK_AREA


area_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_town, pattern="areas")],
    states={
        AREA: [
            CallbackQueryHandler(get_area, pattern="^[0-9]{1,2}$"),
        ],
        CHECK_AREA: [
            CallbackQueryHandler(get_town, pattern="areas"),
            CallbackQueryHandler(get_area, pattern=".*"),
        ],
    },
    fallbacks=[CallbackQueryHandler(end_second_level, pattern="_back")],
    map_to_parent={
        END: NEW_SUBSCRIBE,
    },
)
