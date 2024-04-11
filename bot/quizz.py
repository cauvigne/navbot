"""
This file is part of Navbot.
Navbot is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Navbot is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Foobar. If not, see
<https://www.gnu.org/licenses/>.
"""

import random

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
)


def priority_exercise() -> str:
    mycap = random.randint(1, 359)
    hiscap = random.randint(1, 359)
    if mycap == hiscap:
        hiscap += 10
    beta = (hiscap + 360 - mycap) % 360
    if 180 < beta < 290:
        return (mycap, hiscap, "lui")
    return (mycap, hiscap, "moi")


def priorities(update: Update, context: CallbackContext) -> int:
    global answer
    (mycap, hiscap, answer) = priority_exercise()
    msg = "Je vole au cap %d et à la  même altitude je crois un parapente se dirigeant au cap %d." % (mycap, hiscap)
    reply_keyboard = [["moi", "lui"]]
    update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                    input_field_placeholder="Qui a priorité?"))
    return 3


def priorities_result(update: Update, context: CallbackContext) -> int:
    global answer
    user_answer = update.message.text
    if answer == user_answer:
        msg = "Bonne réponse"
    else:
        msg = "Mauvaise réponse"

    update.message.reply_text(msg)
    return ConversationHandler.END
