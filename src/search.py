import logging
from pathlib import Path

import pandas as pd
import telegram
from diary import get_entry_by_date, send_day_before_and_after
from telegram import Update

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


async def search_by_date(date, diary: pd.DataFrame, update: Update, context, config):
    try:
        entry = get_entry_by_date(date, config, year=True)
    except ValueError:
        logger.error("Date format is not correct")
        await update.message.reply_text(text="Date format is not correct.")
        entry = []

    if len(entry) > 0:
        text = entry["entry"].values[0]
        pretext = f"Here is what you wrote in {entry['date'].dt.date.values[0]}:\n\n"
        text = pretext + text
        await update.message.reply_text(text=text)
        images = entry["images"].values[0]
        if len(images) > 0:
            for image in images:
                with open(Path(config.get("image_dir")) / Path(image), "rb") as f:
                    await update.message.reply_photo(photo=f)
        await send_day_before_and_after(entry, context, config)
    else:

        # searchin for the closest date in the past and in the future
        past = diary[diary["date"] < date].sort_values(by="date", ascending=False)
        future = diary[diary["date"] > date].sort_values(by="date", ascending=True)
        # get the date of the closest entry in the past
        past_date = past["date"].dt.date.values[0].strftime("%d_%m_%Y")
        future_date = future["date"].dt.date.values[0].strftime("%d_%m_%Y")

        answer_text = (
            "No entry for this date. \n"
            "Here are the closest entries:\n"
            f"Before: {past_date}\n"
            f"[/{past_date}]()\n\n"
            f"After: {future_date}\n"
            f"[/{future_date}]()"
        )
        await update.message.reply_text(
            text=answer_text, parse_mode=telegram.constants.ParseMode.MARKDOWN
        )
