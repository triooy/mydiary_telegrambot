import logging
from functools import partial
from pathlib import Path

import commands, os
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
# set env OPENAI_API_KEY to your openai key
os.environ["OPENAI_API_KEY"] = config.get("openai_key")


def main():
    """Start the bot."""
    dispatcher = Application.builder().token(api_key).build()

    dispatcher.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND, partial(process_new_text, config=config)
        )
    )
    dispatcher.add_handler(
        CommandHandler("daily", partial(commands.daily, config=config))
    )
    dispatcher.add_handler(
        CommandHandler("monthly_report", partial(commands.monthly_report, config=config))
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
    dispatcher.add_handler(CommandHandler("report", partial(commands.create_report_for_time, config=config)))

    dispatcher.add_handler(
        CommandHandler("search", partial(commands.search_words, config=config))
    )
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
