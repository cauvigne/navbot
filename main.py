"""
This file is part of Navbot.
Navbot is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Navbot is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Foobar. If not, see
<https://www.gnu.org/licenses/>.
"""

import asyncio
import html
import json
import logging
import sys
import traceback
from functools import wraps

import schedule as schedule
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ApplicationBuilder, filters, ContextTypes, CallbackQueryHandler,
)

from bot import API_TOKEN, USER_IDS, HELP_MSG, \
    USER_INVALID_SYNTAX, bot, BOOKING_PATTERN, INSTANCE, CHAT_ID
from bot.admin_cmd import add_shuttle_cmd, remove_shuttle_cmd, refresh_cmd, status_cmd
from bot.booking.booking_cli import booking_cli
from bot.booking.booking_ui import booking_ui_button_callback
from bot.booking.common import build_pinned_message, post_pin_message_channel
from bot.booking.private_chat import sync_ui_messages
from bot.chatid_mngr import reset_userids_entries
from bot.db import add_spam_id

LOG_PATH = "/var/log/navbot.log"


def exc_handler(exctype, value, tb):
    logger.exception(''.join(traceback.format_exception(exctype, value, tb)))


log_handlers = [logging.FileHandler(filename=LOG_PATH)]
if INSTANCE == "TEST":
    log_handlers.append(logging.StreamHandler(sys.stdout))
else:
    sys.excepthook = exc_handler
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
    handlers=log_handlers
)
logging.getLogger("telegram.vendor.ptb_urllib3.urllib3").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def restricted_user(func):
    """Restrict usage of func to allowed users only and replies if necessary"""

    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.message.from_user.id
        logger.info(
            "username: %s, userid: %s, msg: %s" % (
                update.message.from_user["first_name"], str(user_id), update.message.text))
        if user_id not in USER_IDS:
            await update.message.reply_text('Désolé.Tu n\'es pas autorisé à effectuer cette opération.')
            return  # quit function
        await func(update, context, *args, **kwargs)

    return wrapped


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    print(message)

    # Finally, send the message
    # await context.bot.send_message(
    #     chat_id=TELEGRAM_AUVIGNE_ID, text=message, parse_mode=ParseMode.HTML
    # )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_MSG)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_spam_id(
        " ".join([str(update.message.from_user.first_name), str(update.message.from_user.last_name)]).replace("None",
                                                                                                              ""),
        str(update.message.from_user.username), str(update.message.from_user.id))
    # await post_pin_message(context.bot,update.message.chat_id)
    await update.message.reply_text(build_pinned_message(channel=False)[0], parse_mode=ParseMode.MARKDOWN)
    # When user press start, forget old ui messages
    reset_userids_entries(update.message.from_user.id)
    await sync_ui_messages(context.bot, update.effective_user.id)


# @restricted_user
async def booking_cli_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await booking_cli(update, context)


async def unknown_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Do not answer in the channel
    if update.effective_chat.id != CHAT_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=USER_INVALID_SYNTAX)


async def schedule_8_am():
    logger.info("scheduled update running")
    await post_pin_message_channel(bot)


def main():
    # initializing the bot with API
    application = ApplicationBuilder().token(API_TOKEN).build()

    schedule.every().day.at("08:00").do(schedule_8_am)
    asyncio.get_event_loop().run_until_complete(post_pin_message_channel(bot))

    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('start', start))
    # admin commands
    application.add_handler(CommandHandler("status", status_cmd))
    application.add_handler(CommandHandler("addnav", add_shuttle_cmd))
    application.add_handler(CommandHandler("removenav", remove_shuttle_cmd))
    application.add_handler(CommandHandler("cancelnav", remove_shuttle_cmd))
    application.add_handler(CommandHandler("refresh", refresh_cmd))

    # Button callback
    application.add_handler(CallbackQueryHandler(booking_ui_button_callback))

    application.add_handler(MessageHandler(~filters.COMMAND & filters.Regex(BOOKING_PATTERN), booking_cli_cmd))
    application.add_handler(MessageHandler(filters.COMMAND | ~filters.Regex(BOOKING_PATTERN), unknown_cmd))

    # application.add_error_handler(error_handler)
    # Start the Bot
    application.run_polling(poll_interval=0.5, allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
