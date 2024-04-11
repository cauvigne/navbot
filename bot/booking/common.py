import datetime
import logging

import telegram
from babel.dates import format_date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from bot import HELP_MSG, EMOJI, NB_MAX, NB_MIN, STATUS_LEGEND_MSG, CHAT_ID, PINNED_MSG_ID, BOT_CONTACT_URL
from bot.booking.ui_utils import ui_build_keyboard
from bot.chatid_mngr import get_chat_ids
from bot.db import get_today_shuttle, get_next_shuttles, query_nbseats
from bot.utils import format_notification_msg_channel, format_notification_private

logger = logging.getLogger(__name__)


def build_pinned_message(channel: bool = False):
    msg = ""
    keyboard = [[]]
    hours_str = ""
    if not channel:
        msg += HELP_MSG
    if channel:
        date = format_date(datetime.datetime.now(), format="full", locale="fr_CH")
        if get_today_shuttle() is None:
            hours = []
        else:
            hours = [i for i in get_today_shuttle() if i['datetime'] > datetime.datetime.now()]
        hours_list = []
        if hours is not None:
            for elem in hours:
                if elem['status'] != 'ok':
                    status = "cancelled"
                else:
                    if int(elem['seats'][0]) <= (NB_MAX - NB_MIN):
                        status = "confirmed"
                    else:
                        status = "wait"
                    keyboard.append([])
                    keyboard[-1].append(InlineKeyboardButton(f"+1 {elem['datetime'].strftime('%d-%m %H:%M')}",
                                                             callback_data=f"+1 {elem['datetime'].strftime('%d-%m %H:%M')}"))
                    keyboard[-1].append(InlineKeyboardButton(f"-1 {elem['datetime'].strftime('%d-%m %H:%M')}",
                                                             callback_data=f"-1 {elem['datetime'].strftime('%d-%m %H:%M')}"))
                hours_list += [EMOJI[status] + elem['datetime'].strftime("%H:%M") + " (%s)" % (elem['seats'],)]
            hours_str = ", ".join(hours_list)
        next_shuttle = get_next_shuttles()
        next_shuttle_str = "\n\n"
        if next_shuttle is not None:
            for elem in next_shuttle:
                next_shuttle_str += format_date(elem[0]['datetime'], format="full",
                                                locale="fr_CH").capitalize() + "\n"
                for el in elem:
                    if el['status'] != 'ok':
                        status = "cancelled"
                    else:
                        keyboard.append([])
                        keyboard[-1].append(InlineKeyboardButton(f"+1 {el['datetime'].strftime('%d-%m %H:%M')}",
                                                                 callback_data=f"+1 {el['datetime'].strftime('%d-%m %H:%M')}"))
                        keyboard[-1].append(InlineKeyboardButton(f"-1 {el['datetime'].strftime('%d-%m %H:%M')}",
                                                                 callback_data=f"-1 {el['datetime'].strftime('%d-%m %H:%M')}"))
                        if int(el['seats'][0]) <= (NB_MAX - NB_MIN):
                            status = "confirmed"
                        else:
                            status = "wait"
                    next_shuttle_str += EMOJI[status] + el['datetime'].strftime("%H:%M") + " (%s)" % (el['seats'],)
                next_shuttle_str += "\n\n"
        # next_shuttle_str = "\n\n ".join(
        #     [format_date(i[0], format="full", locale="fr_CH").capitalize() + "\n " + i[1] for i in next_shuttle])
        if hours is not None and len(hours):
            msg += "Aujourd'hui %s  \n%s" % (date, hours_str)
        # else:
        #     msg += "Pas ou plus de navette(s) prévue(s) aujourd'hui."

        if (hours is None or len(hours) == 0) and (next_shuttle is None or len(next_shuttle) == 0):
            msg += "Plus de navette prévue pour l'instant.\n"

        msg += "%s" % (next_shuttle_str,)
        msg += STATUS_LEGEND_MSG
        msg += "Les navettes sont validées dès  %d réservations.  \n" % (NB_MIN,)
        if channel:
            msg += f"Ton espace personnel de réservation est disponible [>>>ici<<<]({BOT_CONTACT_URL}) \n"
            msg += f"Plus d'infos et documentation sur https://asagiri.ch/navette/ "

    return msg, keyboard


async def post_pin_message_channel(tbot):
    try:
        msg, keyboard = build_pinned_message(channel=True)
        await tbot.edit_message_text(msg, chat_id=CHAT_ID, message_id=PINNED_MSG_ID, parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)
    except telegram.error.BadRequest as e:
        if "Message is not modified" in str(e):
            logger.info("Pinned message is up to date")
        else:
            logger.exception("Can not update pinned message.")


async def post_notified_message(bot, tstamp: list):
    try:
        post_msg = format_notification_msg_channel(tstamp)
        await bot.send_message(chat_id=CHAT_ID, text=post_msg, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error("Can not post notified message.", tstamp)


async def update_ui_booking_msg(user_id: int, timest: str, tbot, message_id=None):
    if message_id or (str(user_id) in get_chat_ids().keys() and timest in get_chat_ids()[str(user_id)].keys()):
        try:
            if message_id is None:
                message_id = get_chat_ids()[str(user_id)][timest]
            await tbot.edit_message_text(chat_id=user_id, message_id=message_id,
                                         text=format_notification_private(timest, query_nbseats(timest, user_id)),
                                         reply_markup=InlineKeyboardMarkup(ui_build_keyboard(timest, user_id)),
                                         parse_mode=ParseMode.MARKDOWN)
        except telegram.error.BadRequest as e:
            pass
        except Exception as e:
            logger.exception(str(e))
