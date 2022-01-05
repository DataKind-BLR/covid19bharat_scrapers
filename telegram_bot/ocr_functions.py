import io
import os
import sys
import logging
import scrapers
import telegram
import colorama
import argparse
import traceback
import subprocess

from glob import glob
from contextlib import redirect_stdout
from telegram_bot.util import states_map

colorama.init(strip=True)
CURR_DIR = os.path.abspath('.')


def run_scraper(bot, chat_id, opt):
    # simulate argparse namespace object
    args = argparse.Namespace(
        state_code = opt['state_code'],
        page = None,
        skip_output = False,
        type = opt['type'],
        url = opt['url'] if opt['type'] == 'pdf' else None,
        verbose = False
    )

    dash_log_file = "/tmp/bot_html_output.txt"
    dash_err_file = "/tmp/bot_html_err.txt"

    logging.info(f"Dashboard fetch for {opt['state_code']}")
    try:
        with open(dash_log_file, "w") as log_file:
            bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            logging.info('Running scraper')
            f = io.StringIO()
            with redirect_stdout(f):
                scrapers.run(args)
            p = f.getvalue()
            log_file.write(p)
            logging.info('Scraper run finished')
            log_file.close()

        with open(dash_log_file, "rb") as log_file:
            out = log_file.read()
            if out is not None:
                if len(out) > 4095:
                    log_file.seek(0)
                    bot.send_document(chat_id=chat_id, document=log_file)
                else:
                    bot.send_message(chat_id=chat_id, text=out.decode("utf-8"))

        os.remove(dash_log_file)

    except Exception as e:
        e = traceback.format_exc()
        logging.error(e)
        bot.send_message(chat_id=chat_id, text=e)
        return
