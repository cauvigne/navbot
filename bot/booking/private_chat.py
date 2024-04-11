import logging
from datetime import datetime

from telegram import InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden

from bot.booking.ui_utils import ui_build_keyboard
from bot.chatid_mngr import get_chat_ids, add_to_chatids, del_chat_ids
from bot.db import query_nbseats, get_next_shuttles_timestamp
from bot.utils import format_notification_private, convert_isostr_to_datetime

logger = logging.getLogger(__name__)


async def post_private_notified_message(tbot, user_ids: list, tstamp: list, repost_if_exist: bool = False):
    for i in tstamp:
        for cid in user_ids:
            if not str(cid) in get_chat_ids().keys() or not i in get_chat_ids()[str(cid)]:
                try:
                    post_msg = format_notification_private(i, query_nbseats(i, cid))
                    if repost_if_exist == True or cid not in get_chat_ids().keys() or (
                            cid in get_chat_ids().keys() and i not in get_chat_ids()[cid].keys()):
                        ret = await tbot.send_message(chat_id=cid, text=post_msg, parse_mode=ParseMode.MARKDOWN,
                                                      reply_markup=InlineKeyboardMarkup(ui_build_keyboard(i, cid)))
                        add_to_chatids(i, cid, ret.message_id)  # Add chat id to chat_ids record
                except BadRequest as e:
                    if "Chat not found" in str(e):
                        logger.warning(f"Can not communicate with {cid}")
                except Forbidden as e:
                    if "user is deactivated" in str(e):
                        logger.warning(f"{cid} has been deactivated")
            else:
                try:
                    post_msg = format_notification_private(i, query_nbseats(i, cid))
                    if get_chat_ids():
                        await tbot.edit_message_text(chat_id=cid, text=post_msg, parse_mode=ParseMode.MARKDOWN,
                                                     message_id=get_chat_ids()[str(cid)][i],
                                                     reply_markup=InlineKeyboardMarkup(ui_build_keyboard(i, cid)))
                except BadRequest as e:
                    if "Message to edit not found" in str(e):
                        del_chat_ids(cid, i)
                        await post_private_notified_message(tbot, [cid], [i])


async def sync_ui_messages(tbot, chat_id: [int, str]):
    # Get future shuttles and post message in the chat if needed
    # Also check that message_id still exist if present in the database
    next_shuttles = get_next_shuttles_timestamp()
    if next_shuttles:
        next_shuttles = [i for i in next_shuttles if convert_isostr_to_datetime(i) > datetime.now()]
    await post_private_notified_message(tbot, [str(chat_id)], next_shuttles)
