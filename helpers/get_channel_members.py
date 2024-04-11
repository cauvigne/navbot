"""
This file is part of Navbot.
Navbot is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Navbot is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Foobar. If not, see
<https://www.gnu.org/licenses/>.
"""

from telethon import TelegramClient
from telethon.errors import MultiError

from bot import TELEGRAM_CHANNEL_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_BOT_ID
from bot.db import add_spam_id

client = TelegramClient('xxx', TELEGRAM_API_ID, TELEGRAM_API_HASH)
client.start()

# get all the channels that I can access
channel = {d.entity.username: d.entity
           for d in client.iter_dialogs()
           if d.name == TELEGRAM_CHANNEL_NAME}

# choose the one that I want list users from

i = 0
# get all the users and print them
try:
    for u in client.iter_participants(TELEGRAM_CHANNEL_NAME, aggressive=True):
        user_name = str(u.first_name) + " " + str(u.last_name)
        user_name = user_name.replace('None', '')
        user_contact = str(u.username)
        if str(u.id) != TELEGRAM_BOT_ID:
            print(u.id, u.first_name, u.last_name, u.username)
            add_spam_id(user_name, user_contact, str(u.id))
            i += 1
except MultiError as e:
    print("i=%d. Need to wait 30 sec" % i)
    # time.sleep(30)

# list all sessions
# print(client.session.list_sessions())

# delete current session (current session is associated with `username` variable)
# client.log_out()
