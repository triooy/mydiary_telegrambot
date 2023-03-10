import logging
import sys
from functools import partial
from pathlib import Path

import commands
import openai
from diary import *
from pyhocon import ConfigFactory
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

config = ConfigFactory.parse_file(Path("config/config.conf"))
api_key = config.get("api_key")
openai.api_key = config.get("openai_key")


def main():
    """Start the bot."""
    dispatcher = Application.builder().token(api_key).build()
    # updater = Updater(api_key, use_context=True)
    # dispatcher = updater.dispatcher
    dispatcher.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND, partial(process_new_text, config=config)
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
    dispatcher.add_handler(CommandHandler("pdf", partial(commands.pdf, config=config)))

    dispatcher.add_handler(
        CommandHandler("search", partial(commands.search_words, config=config))
    )
    # Filter dates in the format dd.mm.yyyy or d.m.yyyy or d.m.yy or dd.mm.yy or d.mm.yy or dd.m.yy or d.mm.yyyy or dd.m.yyyy and so on
    # optional dd_mm_yyyy#s-1 or dd_mm_yyyy#s-2 or dd_mm_yyyy#s-3 or dd_mm_yyyy#s-4 or dd_mm_yyyys_5
    dispatcher.add_handler(
        MessageHandler(
            filters.Regex(r"/(\d{1,2}_\d{1,2}_\d{2,4})(s_\d)?"),
            partial(commands.search, config=config),
        )
    )

    dispatcher.add_handler(
        MessageHandler(filters.PHOTO, partial(process_new_photo, config=config))
    )
    logger.info("Bot started")
    dispatcher.run_polling(
        read_timeout=15, timeout=20, connect_timeout=15, write_timeout=15
    )


if __name__ == "__main__":
    main()
