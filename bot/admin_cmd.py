"""
This file is part of Navbot.
Navbot is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Navbot is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Foobar. If not, see
<https://www.gnu.org/licenses/>.
"""

import logging
from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from bot import TELEGRAM_ADMIN_IDS, bot
from bot.booking.common import post_pin_message_channel
from bot.booking.private_chat import post_private_notified_message
from bot.chatid_mngr import clean_chatids
from bot.db import query_add_shuttle, query_remove_shuttle, get_spam_ids, get_next_shuttles_timestamp
from bot.utils import parse_datetime, parse_datetime_multiple, get_shuttle_status

logger = logging.getLogger(__name__)


def restricted_admin(func):
    """Restrict usage of func to allowed users only and replies if necessary"""

    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.message.from_user.id
        logger.info(
            "username: %s, userid: %s, msg: %s" % (
                update.message.from_user["first_name"], str(user_id), update.message.text))
        if user_id not in TELEGRAM_ADMIN_IDS:
            await update.message.reply_text('Désolé.Tu n\'es pas autorisé à effectuer cette opération.')
            return  # quit function
        await func(update, context, *args, **kwargs)

    return wrapped


@restricted_admin
async def add_shuttle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clean_chatids()
    timest = parse_datetime_multiple(context.args)
    if timest is None:
        await update.message.reply_text("Désolé. Le format date-heure est incorrect.")
        return
    await update.message.reply_text('\n'.join([query_add_shuttle(i)['rstatus'] for i in timest]))
    await post_pin_message_channel(bot)
    # await post_notified_message(bot,timest)
    await post_private_notified_message(bot, [i['telegram_id'] for i in get_spam_ids()], timest)


@restricted_admin
async def remove_shuttle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timest = parse_datetime(context.args)
    if timest is None:
        await update.message.reply_text("Désolé. Le format date-heure est incorrect. Exemple: 15-04 10:30")
        return
    await update.message.reply_text(query_remove_shuttle(timest)['rstatus'])
    await post_pin_message_channel(bot)


@restricted_admin
async def refresh_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Refreshing message...")
    await post_pin_message_channel(bot)
    clean_chatids()
    await update.message.reply_text("... done!")


@restricted_admin
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args):
        timest = parse_datetime(context.args)
        res = get_shuttle_status(timest)
        await update.message.reply_text(res["msg"])
    else:
        msg_list = []
        # Return all status
        for tstamp in get_next_shuttles_timestamp():
            msg_list.append(get_shuttle_status(tstamp)["msg"])
        if len(msg_list):
            await update.message.reply_text('\n'.join(msg_list))
        else:
            await update.message.reply_text("pas de navette à venir.\n")
