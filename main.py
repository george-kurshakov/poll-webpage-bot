#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Job
from urllib.request import urlopen
from datetime import timedelta, datetime


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def read_url_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Read the title of a URL."""
    url = update.message.text
    page = urlopen(url).read().decode("latin-1")
    title_index = page.find("<title>")
    start_index = title_index + len("<title>")
    end_index = page.find("</title>")
    title = page[start_index:end_index]
    await update.message.reply_text(title)

async def check_page_update(context: ContextTypes.DEFAULT_TYPE) -> None:

    urls = {"Bioinspired Soft Robotics": "https://www.iit.it/openings?cur=&delta=&type=&position=&location=&selectType=-1&group=MBR002&keywords=&__ncforminfo=2GPlf8FJAgoBbY08M1opDGO3jYxPhq7SlcFnHC7ugetapHnsptlHF_IxZLLzyiyZ2H5jvWlltLKXBf2DTcztHAN4LuX52fIatGVYPLInYnCacQMFjbG1QWm4FuB9KeObzWQV1xs_omqALHSAa4-ptmMSiLyxIk0_ZqBqr12y4LGt1Pr9a87m_6maQptcWIVlqGUYlXUpqFw7l74cQ0uOjVrqtYxBxl8Rdvz8q6eicw90U_I2lPSeVcdnm3N61cBr6U4QT9g-57LGi1bv4jThVaZ7eWy8imSEW-ZbfRojfGnNwMQFEr2r0Dr_qCtn1W__cPeB9Vbj37wRamHp_rGAEr2ybqvzPOC9wSHV-1L0M4r6sYLZWk-mei4VZhu6liNtv2-_LoeD7avK7XZTZ92vsnCJ1oiIO3XIeccYC-n3VHtwgx5s14ncKdYPrlMHoLMQwzbd257DE3JGWNFgrZoZYw%3D%3D",
            "Soft BioRobotics Perception": "https://www.iit.it/openings?cur=&delta=&type=&position=&location=&selectType=-1&group=MBR003&keywords=&__ncforminfo=K_5mlp2ZB06t_9R7Bx9admxmw_tz1679qt35JBviczHJeteBa5hqZmKS5u9ZR-S-y8G3TNTf9LrH1KPkaCijGhii6DNBjP2nJVmjzUa4vNsBU9Z4EthIHc4OZ5GftPT6TvoUKiWeriVreR885cz8x99Qfpw4ykaWdfnDj9us1nxMGAQEF4vUAt4GbK5kqKoDirUs8MeozvuxzD7g-Dg5H5vljFxO3osYk2aRJ_4vGFMKLtj6VyN_DdexCn5hzHBbEuZOze8Ib7cvPNoS9xvBqVDnjL7zWlzJJRCYrx6O2ff1zTfyslcKaAGov0Ewzz95NUuC2M-JDtgJQJ6KifOkWYmEoZMAnZG62sxenzjW8llZFduSFgB9BjMoPIgi7cHaKcXkwFvgj6zcitpyr-0td-1pYyB1opWmJb50zSmxE9uLtupPYWSPfmmqZStW68H-qWWviYwUtGyPksCBLRwLtw%3D%3D",
            "Soft Robotics for Human Cooperation and Rehabilitation": "https://www.iit.it/openings?cur=&delta=&type=&position=&location=&selectType=-1&group=REH002&keywords=&__ncforminfo=VDM0Lw5a82ItzrRHOPJ0G64y30zHYI1wTa7B8aEe_MFbGjEb7XsreGDuJcLE4szN23hw9K7fjAxD8KwMhsCm8YUYq-13kAmKmIYaZsT73QczduI5fwFa8PWE9NGP1PlYSAkcjce_45d-G12BZGiVUXOwsDZDsy_oJWzJn0DM6onw8X5ECMrDdoRPcFuwlgP5ifAhFu1s7KV9Qkh1DbU5_dZePNdVUY_DKBWrzr65LwWWWE9RMOnWleIprII5OC_rMBW2qK-o_cnpPqvsMjwW3V8Tchn5rJmY85LYNruXZ_iPPq9u3kZtiR2um7FqecfI4Tu3o8tYcp8mk9ju3uEOTSFS5YWYyo_TuTH7ITJaHc_nRPpFQkzl4gIhqaTPfjNhGjo0wMD0RzkTtVQStyLNxbsivLSMJoFhxCgfJOcjsF6u3KlAtLrHo-Cqh7Wy8v1YcrBnMuN1QcLd6OVGroXsPw%3D%3D",
            }
    message = ""
    for name, url in urls.items():
        page = urlopen(url).read().decode("latin-1")
        if "No openings" in page:
            message += f"*{name}*: No openings found.\n\n"
        else:
            message += f"*{name}*: Openings found!\n\n"

    message += f"Last checked: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    await context.bot.send_message(chat_id=context.job.data, text=message, parse_mode="markdown")

async def monitor_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Monitor a URL for updates."""
    # url = update.message.text.split(" ")[1]W
    context.job_queue.run_repeating(check_page_update, interval=timedelta(minutes=10), first=0, data=update.effective_chat.id)
    await update.message.reply_text(f"Monitoring url for updates...")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    token_file = os.environ.get("TOKEN_FILE")
    with open(token_file) as f:
        token = f.read().strip()
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("monitor_url", monitor_url))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, read_url_title))

    # application.job_queue.run_repeating(check_page_update, interval=timedelta(seconds=10), first=0)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()