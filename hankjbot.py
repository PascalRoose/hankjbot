#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#   hankjbot made by Pascal Roose
#


import os
import logging
import json
import random

from dotenv import load_dotenv
from telegram.ext import CommandHandler, InlineQueryHandler, Updater
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

# Load .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Load variables from .env
token = str(os.environ.get('TOKEN'))
admin_tgid = int(os.environ.get('ADMIN_TGID'))
puns_file = str(os.environ.get('PUNS_FILE'))
puns_thumb = str(os.environ.get('PUNS_THUMB'))

# Initialize list of hank puns
hankpuns = []


def load_hankpuns():
    with open(puns_file) as json_file:
        global hankpuns
        hankpuns = json.load(json_file)


def add_hankpun(newpun_text):
    newpun_id = hankpuns[-1]['id'] + 1

    newpun = {
        "id": newpun_id,
        "pun": newpun_text
    }
    hankpuns.append(newpun)

    with open(puns_file, 'w') as json_file:
        json.dump(hankpuns, json_file)
    load_hankpuns()


def remove_hankpun(pun_id):
    for hankpun in hankpuns:
        if hankpun['id'] == pun_id:
            hankpuns.remove(hankpun)
            with open(puns_file, 'w') as json_file:
                json.dump(hankpuns, json_file)
            load_hankpuns()
            return hankpun
    return False


# Send welcome message
def start_command(_bot, update):
    if update.message.chat.type == 'private':
        update.message.reply_text(
            'Hi, im Hank Johnson!\n'
            '\n'
            'You can use me in groups or in direct messages by typing @hankjbot, '
            'I will then tell you a hilarious pun with my name.'
        )


def help_command(_bot, update):
    if update.message.chat.type == 'private':
        if update.message.from_user.id == admin_tgid:
            update.message.reply_text(
                'List of commands:\n'
                '/list - Lists all puns Hank knows'
                '/add <Text> - Add a new pun\n'
                '/remove <Pun ID> - Remove a pun'
            )


def list_command(_bot, update):
    if update.message.chat.type == 'private':
        if update.message.from_user.id == admin_tgid:
            message = 'List of all puns:\n'
            for hankpun in hankpuns:
                message += f'{hankpun["id"]}. {hankpun["pun"]}\n'
            update.message.reply_text(message)


# Add a new hank pun
def add_command(_bot, update):
    if update.message.chat.type == 'private':
        if update.message.from_user.id == admin_tgid:
            pun = update.message.text.strip('/add ')
            add_hankpun(pun)
            update.message.reply_text(
                'Thanks for this new pun. I\'ll be sure to use it!'
            )


# Remove one of the hank puns
def remove_command(_bot, update):
    if update.message.chat.type == 'private':
        if update.message.from_user.id == admin_tgid:
            pun_id = update.message.text.strip('/remove ')
            try:
                pun_id = int(pun_id)
                result = remove_hankpun(pun_id)
                if result is False:
                    update.message.reply_text(
                        f'Hankpun with id: {pun_id} was not found'
                    )
                else:
                    update.message.reply_text(
                        f'The following pun was removed:\n'
                        f'{result["pun"]}'
                    )
            except ValueError:
                update.message.reply_text(
                    'ID is not an integer. Example:\n'
                    '/remove 1'
                )


# Handle the inline query. Pick a random hank pun
def inlinequery(_bot, update):
    random_hankpun = random.choice(hankpuns)
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Hank Johnson says: ",
            description=random_hankpun['pun'],
            input_message_content=InputTextMessageContent(random_hankpun['pun']),
            thumb_url=puns_thumb
        )
    ]
    update.inline_query.answer(results)


def error(_bot, update, tg_error):
    # Log Errors caused by Updates.
    logging.warning(f'Update "{update}" caused error "{tg_error}"')


def main():
    # Get all puns from hankpuns.json
    load_hankpuns()

    # Setup the updater for receiving telegram update messages
    updater = Updater(token, request_kwargs={'read_timeout': 6, 'connect_timeout': 7})

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers to dispatcher
    dp.add_error_handler(error)

    # Private chat handlers
    dp.add_handler(CommandHandler(command="start", callback=start_command))
    dp.add_handler(CommandHandler(command="help", callback=help_command))
    dp.add_handler(CommandHandler(command="list", callback=list_command))
    dp.add_handler(CommandHandler(command="add", callback=add_command))
    dp.add_handler(CommandHandler(command="remove", callback=remove_command))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # Start polling to TG servers
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
