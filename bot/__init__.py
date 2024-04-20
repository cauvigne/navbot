"""
This file is part of Navbot.
Navbot is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Navbot is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Foobar. If not, see
<https://www.gnu.org/licenses/>.
"""

import json
import os

import telegram
from dotenv import load_dotenv

load_dotenv()

INSTANCE = os.environ.get("INSTANCE")

# Telegram bot environment variables
API_TOKEN = os.environ.get('API_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Database environment variables
DB_HOST = os.environ.get('DB_HOST')
DB_DATABASE = os.environ.get('DB_DATABASE')
DB_USER = os.environ.get('DB_USER')
DB_PWD = os.environ.get('DB_PWD')
DB_PORT = os.environ.get('DB_PORT')
BOT_CONTACT = os.environ.get('BOT_CONTACT')

# Telethon api environment variables
TELEGRAM_API_ID = os.environ.get('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH')

TELEGRAM_CHANNEL_NAME = os.environ.get('TELEGRAM_CHANNEL_NAME')
TELEGRAM_CHANNEL_NAME_PROD = os.environ.get('TELEGRAM_CHANNEL_NAME_PROD')  # For theleton utility
TELEGRAM_ADMIN_IDS = json.loads(os.environ.get('TELEGRAM_ADMIN_IDS'))
TELEGRAM_BOT_ID = os.environ.get('TELEGRAM_BOT_ID')
# Minimum people number in the shuttle
NB_MIN = 4
# Maximum people number in the shuttle
NB_MAX = 8
# Max time prior the shuttle time to perform a reservation (in minutes)
TIMEOUT_SHUTTLE = 1

CHANNEL_POST_URL = f"https://t.me/c/{CHAT_ID[4:]}"  # /{PINNED_MSG_ID}"
BOT_CONTACT_URL = f"https://t.me/{BOT_CONTACT[1:]}"

HELP_MSG = f"""Bienvenue dans ton espace personnel des réservations des navettes d\'Asagiri.
Utilise les boutons +- à disposition pour réserver une navette. 

Consulte en temps réel le statut et infos utiles de toutes les navettes sur le canal [Bus Asagiri]({CHANNEL_POST_URL}).


_Conservateur? Tu peux toujours utiliser l'ancienne syntaxe:_
+2 10:30 pour *réserver* *2* places *aujourd'hui* à *10h30*
+2 05-04 10:30 pour *réserver* *2* places le *5 avril* à *10h30*
-2 10:30 pour *annuler* *2* places à *10h30* """

EMOJI = {"cancelled": "\U0000274C", "wait": "\U0001F535", "confirmed": "\U00002705"}
STATUS_LEGEND_MSG = f"""Légende:
{EMOJI["confirmed"]} : Confirmé, {EMOJI["cancelled"]}: Annulé, {EMOJI["wait"]} : En attente (pas encore assez de réservations)

"""

USER_INVALID_SYNTAX = 'Message invalide. Utilise la syntaxe type: +1 10:30  (pour aujourd\'hui) ou +1 22-05 10:30'

USER_IDS = TELEGRAM_ADMIN_IDS + []

PINNED_MSG_ID = os.environ.get('PINNED_MSG_ID')

BOOKING_PATTERN = r" *([+-]) *(\d+) *((\d{1,2} *[-/] *\d{1,2} )? *\d{1,2} *[hH:.] *\d{1,2})"

bot = telegram.Bot(API_TOKEN)
