from os import stat
import telegram
import subprocess
import os
import shlex
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram_bot.util import build_menu, ocr_dict, pdf_dict, dash_dict, states_map
from telegram_bot.ocr_functions import ocr1, ocr2, pdf, dashboard, ka_detail, run_scraper
import json
import logging

def entry(bot, update):

    if update.message:
        if update.message.text.startswith("/test"):
            update.message.reply_text("200 OK!", parse_mode=telegram.ParseMode.MARKDOWN)
            return

        if update.message.text.startswith("/start"):
            button_list = []
            for st_name in states_map.keys():
                button_list.append(
                    InlineKeyboardButton(
                        st_name, callback_data=states_map[st_name]
                    )
                )
            reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
            bot.send_message(
                chat_id=update.message.chat.id,
                text="Which state do you want to fetch data for?",
                reply_to_message_id=update.message.message_id,
                reply_markup=reply_markup,
            )
            return

        if update.message.text.startswith("/help"):
            help_text = f"""
            \n*Steps on how to run the bot to fetch data from state bulletins*
            1 `/start` will start the data fetching process
            2 Choose a state you want to enter data for
            3 Follow instructions to upload image or a PDF or call the dashboard url
            4 Copy & paste the output difference that needs to be entered in excel sheet
            \n\n_Send `/test` for checking if the bot is online_"""

            update.message.reply_text(
                str(help_text), parse_mode=telegram.ParseMode.MARKDOWN
            )
            return
