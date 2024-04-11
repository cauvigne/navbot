"""
This file is part of Navbot.
Navbot is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Navbot is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Foobar. If not, see
<https://www.gnu.org/licenses/>.
"""

import datetime
import logging

from bot.db import set_private_msg_ids, get_private_msg_ids
from bot.utils import convert_isostr_to_datetime

logger = logging.getLogger(__name__)


def add_to_chatids(tstamp: str, cid: [int, str], message_id: int):
    chat_ids = get_private_msg_ids()
    cid = str(cid)
    if cid not in chat_ids.keys():
        chat_ids[cid] = {}
    chat_ids[cid][str(tstamp)] = message_id
    save_chatids(chat_ids)


def clean_chatids():
    chat_ids = get_private_msg_ids()
    # Remove past shuttles from this list
    if chat_ids:
        for elem in chat_ids.keys():
            chat_ids[elem] = {k: v for k, v in chat_ids[elem].items() if
                              convert_isostr_to_datetime(k) > datetime.datetime.now()}
        save_chatids(chat_ids)


def reset_userids_entries(user_id):
    chat_ids = get_private_msg_ids()
    if chat_ids and str(user_id) in chat_ids.keys():
        del chat_ids[str(user_id)]
    save_chatids(chat_ids)


def save_chatids(chat_ids: dict):
    set_private_msg_ids(chat_ids)


def get_chat_ids():
    ids = get_private_msg_ids()
    if ids is None:
        ids = {}
    return ids


def del_chat_ids(cid, i):
    chat_ids = get_private_msg_ids()
    del chat_ids[cid][i]
    set_private_msg_ids(chat_ids)
