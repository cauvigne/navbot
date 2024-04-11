from datetime import datetime

import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot import CHAT_ID, TIMEOUT_SHUTTLE, bot
from bot.booking.booking_cli import parse_reservation
from bot.booking.common import update_ui_booking_msg, post_pin_message_channel
from bot.booking.private_chat import post_private_notified_message
from bot.chatid_mngr import add_to_chatids, get_chat_ids
from bot.db import query_book_shuttle
from bot.utils import parse_datetime_str, build_user

logger = logging.getLogger(__name__)

async def booking_ui_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mid = None
    query = update.callback_query
    res = parse_reservation(query.data)
    if res is None:
        logger.error("Error in booking_ui, invalid timestamp")
        await query.answer()
        return
    timest = parse_datetime_str(res["timest"])
    if datetime.strptime(timest,
                         '%Y-%m-%d %H:%M').timestamp() - datetime.now().timestamp() < TIMEOUT_SHUTTLE * 60:
        if str(update.effective_message.chat_id) != CHAT_ID:
            # We are in private chat now
            await query.edit_message_text("Cette navette est déja passée.")
        else:
            # We are in the channel
            pass
    else:
        if str(update.effective_message.chat_id) != CHAT_ID:
            # We are in a private chat
            mid = query.message.message_id
            # Add chat id to chat_ids record if not done yet
            add_to_chatids(timest, update.effective_user.id, query.message.message_id)
        else:
            # We are in the channel chat
            if not str(update.effective_user.id) in get_chat_ids().keys() or (str(update.effective_user.id) in get_chat_ids().keys() and timest not in get_chat_ids()[str(update.effective_user.id)].keys()):
                await post_private_notified_message(bot, [update.effective_user.id], [timest])
        query_book_shuttle(timest, build_user(update.effective_user),
                                    res["fct"] + str(res["nb"]), str(update.effective_user.id))



        await update_ui_booking_msg(query.from_user.id, timest, context.bot, message_id=mid)

    await post_pin_message_channel(bot)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()