#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import logging
import telegram

from time import sleep
from telegram_bot.entry import entry
from telegram.error import NetworkError, Unauthorized

COVID_BOT_TOKEN='2057487700:AAFsjn8Jc9QDw6q4cCk9YjL2Q6_7xJv3cKk'
VISIONAPI_TOKEN='91c256a14c3b399081bbeac9348cf0627643184f'
LIFESPAN = 1200 # How long the container exist

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger('Start_Bot')

# try:
#     # COVID_BOT_TOKEN = os.environ["COVID_BOT_TOKEN"]
#     COVID_BOT_TOKEN='2057487700:AAFsjn8Jc9QDw6q4cCk9YjL2Q6_7xJv3cKk'
# except KeyError:
#     logger.error("Bot credentials not found in environment")

# try:
#     # If the token is available in the environment, print it to a file
#     VISIONAPI_TOKEN = os.environ["VISIONAPI_TOKEN"]
#     # TODO: Find a better fix
#     print("Creating visionapi.json at : " + os.path.dirname(os.path.realpath(__file__)))
#     with open("visionapi.json", "w") as f:
#         print(VISIONAPI_TOKEN, file=f)
# except KeyError:
#     logger.error("VisionAPI credentials not found in environment")


def main():
    """Run the bot @datakind_covid19bharat_bot."""
    try:
        update_id = int(os.environ["UPDATE_ID"])
    except:
        update_id = 0

    start_time = int(time.time())
    formatted_time = time.ctime(start_time)
    logger.info(f"Bot started at {formatted_time}")
    bot = telegram.Bot(COVID_BOT_TOKEN)

    while True:
        try:
            logger.info('Bot is at your service, I am listening....')
            import pdb
            pdb.set_trace()
            for update in bot.get_updates(offset=update_id, timeout=10):
                update_id = update.update_id + 1
                logger.info(f"Update ID:{update_id}")
                entry(bot, update)
        except NetworkError:
            logger.info('Network Error --->', NetworkError)
            sleep(1)
        except Unauthorized:
            logger.info('Unauthorized --->', Unauthorized)
            update_id += 1  # The user has removed or blocked the bot.

        if int(time.time()) - start_time > LIFESPAN:
            logger.info('Enough for the day! Passing on to next Meeseek')
            with open('/tmp/update_id', 'w') as the_file:
                the_file.write(str(update_id))
            break


if __name__ == "__main__":
    main()
