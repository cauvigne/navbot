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

import telegram
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot import CHAT_ID, NB_MAX
from bot.booking.common import build_pinned_message

logger = logging.getLogger(__name__)


def post_message(context, msg: str, pinned: bool = False):
    context.bot.send_message(CHAT_ID, msg, disable_notification=True)


def post_confirmation(context: ContextTypes.DEFAULT_TYPE, nb: int, hour: str, confirmation: bool):
    """
    :param confirmation: confirmation of the shuttle for the given hour
    :param nb: Number of people in the shuttle
    :param hour: hour of the shuttle
    """
    if confirmation:
        msg = "La navette de %s est confirmée. %d personnes inscrites, %d places libres." % (
            hour, nb, NB_MAX - nb)
    else:
        msg = "La navette de %s est annulée." % (hour,)
    post_message(context, msg)


async def post_pin_message(bot, chat_id: [int, str]):
    try:
        msg = build_pinned_message(channel=False)
        await bot.unpin_all_chat_messages(chat_id)
        res = await bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN,
                                     disable_notification=True)
        await bot.pin_chat_message(chat_id, res.message_id)
    except telegram.error.BadRequest:
        pass


async def send_message(bot, msg: str, ids: list):
    nb_chat_not_found = 0
    for id_user in ids:
        try:
            bot.send_message(chat_id=id_user, text=msg, parse_mode=ParseMode.MARKDOWN)
        except telegram.error.BadRequest as e:
            if "Chat not found" in str(e):
                nb_chat_not_found += 1
                # logger.error("Can not send private message to %s" % str(id_user))
            else:
                logger.exception("Can not send message.")
        if nb_chat_not_found:
            logger.info(f"{nb_chat_not_found} chat not found")


### helpers ###
async def nonslash_sendreply_with_log(update: Update, msg: str) -> None:
    logger.info("bot>%s" % update.message.from_user.id + " : " + msg)
    await update.message.reply_text(msg)


if __name__ == "__main__":
    msg = build_pinned_message(channel=True)
