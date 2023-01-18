import logging
import sys
from functools import partial
from pathlib import Path

import commands
from diary import *
from pyhocon import ConfigFactory
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

config = ConfigFactory.parse_file(Path("config/config.conf"))
api_key = config.get("api_key")


def main():
    """Start the bot."""
    updater = Updater(api_key, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command, partial(process_new_text, config=config)
        )
    )
    dispatcher.add_handler(
        CommandHandler("daily", partial(commands.daily, config=config))
    )
    dispatcher.add_handler(
        CommandHandler("random", partial(commands.get_random_entry, config=config))
    )
    dispatcher.add_handler(
        CommandHandler("get_data", partial(commands.get_data, config=config))
    )
    dispatcher.add_handler(
        CommandHandler("stats", partial(commands.get_stats, config=config))
    )
    dispatcher.add_handler(
        CommandHandler("help", partial(commands.help, config=config))
    )
    dispatcher.add_handler(
        MessageHandler(Filters.photo, partial(process_new_photo, config=config))
    )
    updater.start_polling()
    logger.info("Bot started")
    updater.idle()


if __name__ == "__main__":
    main()
