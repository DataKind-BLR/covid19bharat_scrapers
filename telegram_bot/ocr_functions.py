import subprocess
import sys
import telegram
import os
import logging
import traceback
import io
import colorama

from contextlib import redirect_stdout
from glob import glob
from telegram_bot.util import states_map
import scrapers
CURR_DIR = os.path.abspath('.')

class Args:
  pass

colorama.init(strip=True)

def run_scraper(bot, chat_id, state_code, url_type, url):
    '''
    trigger scraper.py from here...
    '''
    args = Args()
    args.state_code = state_code
    args.page = None
    args.skip_output = True
    args.type = url_type
    args.url = None
    if url_type == 'pdf':
        args.url = url
        
    dash_log_file = "/tmp/bot_html_output.txt"
    dash_err_file = "/tmp/bot_html_err.txt"

    logging.info(f"Dashboard fetch for {state_code}")
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

