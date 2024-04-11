from datetime import datetime
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from bot.db import query_nbseats, query_free_seats_nb, get_next_shuttles_timestamp


def ui_build_keyboard(timest: str, user_id: str) -> InlineKeyboardMarkup:
    keyboard = [[]]
    tstamp_dt = datetime.strptime(timest, '%Y-%m-%d %H:%M').strftime('%d-%m %H:%M')
    my_booking = query_nbseats(timest, user_id)
    if query_free_seats_nb(timest) > 0:
        keyboard[0].append(InlineKeyboardButton("+1", callback_data=f"+1 {tstamp_dt}"))
    if my_booking > 0:
        keyboard[0].append(InlineKeyboardButton("-1", callback_data=f"-1 {tstamp_dt}"))
    return keyboard
