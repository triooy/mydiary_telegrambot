import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import telegram
from diary import get_diary
from telegram import Update

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


async def send_day_before_and_after(entry, context, config):
    # send dates day before and after
    diary = get_diary(config)
    # entry is a Series object convert to pandas DataFrame
    if isinstance(entry, pd.Series):
        entry = pd.DataFrame(entry).T
    entry_date = pd.to_datetime(entry["date"].values[0]).strftime("%d_%m_%Ys_1")
    daybefore, dayafter = get_closest_entries(entry["date"].values[0], diary)
    msg = (
        f"Here are the closest entries:\n"
        f"Similar entry for today: /{entry_date}\n"
        f"Before: /{daybefore}\n"
        f"After: /{dayafter}"
    )
    await context.bot.send_message(chat_id=config.get("chat_id"), text=msg)


def get_entry_by_date(date, config, year=False):
    """Get the diary entry for the given date."""
    # get the diary entry for the given month and day
    if isinstance(date, str):
        date = datetime.strptime(date, "%d.%m.%Y").date()

    diary = get_diary(config=config)
    if year:
        diary_date = diary[
            (diary["date"].dt.day == date.day)
            & (diary["date"].dt.month == date.month)
            & (diary["date"].dt.year == date.year)
        ]
    else:
        diary_date = diary[
            (diary["date"].dt.day == date.day)
            & (diary["date"].dt.month == date.month)
            & (diary["date"].dt.year != date.year)
        ]
    return diary_date


def get_closest_entries(date, diary):
    if isinstance(date, str):
        date = datetime.strptime(date, "%d.%m.%Y")
    past = diary[diary["date"] < date].sort_values(by="date", ascending=False)
    future = diary[diary["date"] > date].sort_values(by="date", ascending=True)
    # get the date of the closest entry in the past
    if len(past) == 0:
        past_date = "No entry"
    else:
        past_date = past["date"].dt.date.values[0].strftime("%d_%m_%Y")
    if len(future) == 0:
        future_date = "No entry"
    else:
        future_date = future["date"].dt.date.values[0].strftime("%d_%m_%Y")
    return past_date, future_date


async def search_by_date(
    date, diary: pd.DataFrame, update: Update, context, config, send=True
):
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
        if send:
            await update.message.reply_text(text=text)
            images = entry["images"].values[0]
            if len(images) > 0:
                for image in images:
                    with open(Path(config.get("image_dir")) / Path(image), "rb") as f:
                        await update.message.reply_photo(photo=f)
            await send_day_before_and_after(entry, context, config)
    else:

        past_date, future_date = get_closest_entries(date, diary)

        answer_text = (
            "No entry for this date. \n"
            "Here are the closest entries:\n"
            f"Before: {past_date}\n"
            f"[/{past_date}]()\n\n"
            f"After: {future_date}\n"
            f"[/{future_date}]()"
        )
        if send:
            await update.message.reply_text(
                text=answer_text, parse_mode=telegram.constants.ParseMode.MARKDOWN
            )
    return entry
