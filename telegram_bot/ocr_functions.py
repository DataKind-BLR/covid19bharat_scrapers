import subprocess
import sys
import telegram
import os
import logging
import traceback

from glob import glob
from telegram_bot.util import states_map
CURR_DIR = os.path.abspath('.')

def run_scraper(bot, chat_id, state_code, url_type, url):
    '''
    trigger scraper.py from here...
    '''
    if url_type == 'image':
        cmd = ["python", "scrapers.py", "--state_code", state_code, '--type' , 'image', '--url', url]
    elif url_type == 'pdf':
        # TODO - get page number from user and scan for that...
        cmd = ["python", "scrapers.py", "--state_code", state_code, '--type' , 'pdf', '--url', url]
    elif url_type == 'html':
        # command will read the dashboard url specified in `states.yaml` file by directly
        cmd = ["python", "scrapers.py", "--state_code", state_code]

    dash_log_file = "/tmp/bot_html_output.txt"
    dash_err_file = "/tmp/bot_html_err.txt"

    logging.info(f"Dashboard fetch for {state_code}")
    try:
        with open(dash_log_file, "w") as log_file:
            with open(dash_err_file, "w") as err_file:
                bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                logging.info('I am yet to run subprocess')
                p = subprocess.run(
                    cmd,
                    cwd=CURR_DIR,
                    stdout=log_file,
                    stderr=err_file,
                    encoding="utf8",
                    timeout=20
                )
                logging.info('After subprocess')

    except Exception as e:
        e = traceback.format_exc()
        logging.error(e)
        bot.send_message(chat_id=chat_id, text=e)
        return

    with open(dash_log_file, "rb") as log_file:
        with open(dash_err_file, "rb") as err_file:
            out = log_file.read()
            err = err_file.read()
            try:
                # Send the errata
                if err is not None:
                    if len(err) > 4095:
                        bot.send_document(chat_id=chat_id, document=err_file)
                    else:
                        bot.send_message(chat_id=chat_id, text=err.decode("utf-8"))
                os.remove(dash_err_file)
            except Exception as e:
                logging.error(e)
                pass

            try:
                # Send the results
                if out is not None:
                    if len(out) > 4095:
                        log_file.seek(0)
                        bot.send_document(chat_id=chat_id, document=log_file)
                    else:
                        bot.send_message(chat_id=chat_id, text=out.decode("utf-8"))
                    os.remove(dash_log_file)
            except Exception as e:
                logging.error(e)
                pass
