from pyhocon import ConfigFactory
from pathlib import Path
import sys 
from diary import *
import commands
from functools import partial

from telegram.ext import (
    Updater,
    MessageHandler,
    Filters,
    CommandHandler,
)
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

config = ConfigFactory.parse_file(Path('config/config.conf'))
api_key = config.get('api_key')

def main():
    """Start the bot."""
    updater = Updater(api_key, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, partial(process_new_text, config=config)))
    dispatcher.add_handler(CommandHandler("daily", partial(commands.daily, config=config)))
    dispatcher.add_handler(CommandHandler("random", partial(commands.get_random_entry, config=config)))
    dispatcher.add_handler(MessageHandler(Filters.photo, partial(process_new_photo, config=config)))
    updater.start_polling()
    logger.info("Bot started")
    updater.idle()
    
if __name__ == "__main__":
    main()