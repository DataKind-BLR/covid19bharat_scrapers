#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import telegram
from telegram.error import NetworkError, Unauthorized
import time
from time import sleep
import os
from telegram_bot.entry import entry
import json

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("Start_Bot")

try:
    COVID_BOT_TOKEN = os.environ["COVID_BOT_TOKEN"]
    
except KeyError:
    logger.error("Bot credentials not found in environment")
try:
    # If the token is available in the environment,
    # print it to a file
    VISIONAPI_TOKEN = os.environ["VISIONAPI_TOKEN"]
    # TODO: Find a better fix 
    print("Creating visionapi.json at : " + os.path.dirname(os.path.realpath(__file__)))
    with open("visionapi.json", "w") as f:
        print(VISIONAPI_TOKEN, file=f)

except KeyError:
    logger.error("VisionAPI credentials not found in environment")

# How long the container exist
LIFESPAN = 3600


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
            for update in bot.get_updates(offset=update_id, timeout=10):
                update_id = update.update_id + 1
                logger.info(f"Update ID:{update_id}")
                entry(bot, update)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1
        if int(time.time()) - start_time > LIFESPAN:
            logger.info("Enough for the day! Passing on to next Meeseek")
            with open("/tmp/update_id", "w") as the_file:
                the_file.write(str(update_id))
            break


if __name__ == "__main__":
    main()
