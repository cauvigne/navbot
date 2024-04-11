from datetime import datetime

import re

from telegram import Update
from telegram.ext import ContextTypes
import logging

from bot import USER_INVALID_SYNTAX, BOOKING_PATTERN, TIMEOUT_SHUTTLE
from bot.booking.common import post_pin_message_channel, update_ui_booking_msg
from bot.db import query_book_shuttle
from bot.reservation import nonslash_sendreply_with_log
from bot.utils import build_user, parse_datetime_str

logger = logging.getLogger(__name__)

async def booking_cli(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    msg = update.message.text
    user = build_user(update.message.from_user)
    logger.info(
        "username: %s, userid: %s, msg: %s" % (
            user, str(update.message.from_user.id), update.message.text))
    res = parse_reservation(msg)
    if res is None:
        await nonslash_sendreply_with_log(update, USER_INVALID_SYNTAX)
        return
    timest = parse_datetime_str(res["timest"])
    if timest is None:
        await nonslash_sendreply_with_log(update, USER_INVALID_SYNTAX)
    else:
        if datetime.strptime(timest,
                             '%Y-%m-%d %H:%M').timestamp() - datetime.now().timestamp() < TIMEOUT_SHUTTLE * 60:
            await nonslash_sendreply_with_log(update, "Il est trop tard pour réserver cette navette, désolé.")
            return
        res_db = query_book_shuttle(timest, user,
                                    res["fct"] + str(res["nb"]), str(update.message.from_user.id))
        if res_db is not None and "OK" in res_db["msg"].upper():
            if res["fct"] == "+":
                await nonslash_sendreply_with_log(update,
                                                  "Merci %s. Tu as réservé %d place(s) dans la navette de %s. Le statut temps réel (confirmé, annulé, ...) de la navette sont disponible sur le canal Bus Asagiri." % (
                                                      user, res["nb"], res["timest"]))
            else:
                await nonslash_sendreply_with_log(update,
                                                  "Merci %s. tu as annulé %d place(s) dans la navette de %s." % (
                                                      user, res["nb"], res["timest"]))
            await post_pin_message_channel(context.bot)
            # Try to modify message with buttons
            await update_ui_booking_msg(update.effective_user.id, str(timest), context.bot)
            # Spam E. Laforge
            # res = get_shuttle_status(timest)
            # if res["status"] == "ok":
            #     if INSTANCE == "PROD":
            #         await context.bot.send_message(chat_id=TELEGRAM_LAFORGE_ID, text="nouveau statut:\n"+res["msg"])
            #     else:
            #         await context.bot.send_message(chat_id=TELEGRAM_AUVIGNE_ID, text=res["msg"])
        elif res_db is not None:
            await context.bot.send_message(chat_id=update.message.chat_id, text=res_db["msg"])
        else:
            await update.message.reply_text("Une erreur imprévue est survenue.")

def parse_reservation(msg: str):
    res = re.match(BOOKING_PATTERN, msg)
    if res is None:
        return None
    timestamp = re.sub(' *[-/] *', '-', res[3])
    timestamp = re.sub(' *[h:.H] *', ':', timestamp)
    return {"fct": res[1], "nb": int(res[2]), "timest": timestamp}