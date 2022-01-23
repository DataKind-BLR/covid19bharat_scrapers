import io
import os
import logging
import scrapers
import telegram
import colorama
import argparse
import traceback

from contextlib import redirect_stdout

colorama.init(strip=True)
LOG_FILE = os.path.join("/", "tmp", "bot_output.txt")

def run_scraper(bot, chat_id, opt):
    # simulate argparse namespace object

    args = {
        'state_code': opt['state_code'],
        'page': opt['page'] if 'page' in opt else None,
        'skip_output': opt['skip_output'] if 'skip_output' in opt else False,
        'type': opt['type'],
        'url': opt['url'] if opt['type'] == 'pdf' else None,
        'verbose': opt['verbose'] if 'verbose' in opt else None
    }

    logging.info(f"Dashboard fetch for {opt['state_code']}")
    try:
        with open(LOG_FILE, "w") as log_file:
            bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            logging.info('Running scraper')
            f = io.StringIO()
            with redirect_stdout(f):
                scrapers.run(args)
            p = f.getvalue()
            log_file.write(p)
            logging.info('Scraper run finished')
            log_file.close()

        with open(LOG_FILE, "rb") as log_file:
            out = log_file.read()
            if out is not None:
                if len(out) > 4095:
                    log_file.seek(0)
                    bot.send_document(chat_id=chat_id, document=log_file)
                else:
                    bot.send_message(chat_id=chat_id, text=out.decode("utf-8"))
        # os.remove(LOG_FILE)

    except Exception as e:
        e = traceback.format_exc()
        logging.error(e)
        bot.send_message(chat_id=chat_id, text=e)
        return
