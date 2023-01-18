import ast
import logging
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from telegram import Update
from telegram.ext import CallbackContext

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def create_diary_entry(text, insert_time=True):
    """Create a new diary entry for the user with the given text."""
    # create a new diary entry
    # get current date
    date = datetime.now()
    time_ = datetime.now().strftime("-- %H:%M --")
    if insert_time:
        text = time_ + "\n" + str(text) + "\n"
    else:
        text = "\n" + str(text) + "\n"
    df = pd.DataFrame({"date": [date], "entry": [text], "images": [[]]})
    logger.info(f"New diary entry created: {df}")
    return df


def get_diary(config):
    """Get the diary of the user."""
    # get the diary of the user
    df = pd.read_csv(config.get("diary_csv"))
    df["images"] = df["images"].apply(ast.literal_eval)
    df["date"] = pd.to_datetime(df["date"])
    df["entry"] = df["entry"].astype(str)
    return df


def get_entry_by_date(date, config):
    """Get the diary entry for the given date."""
    # get the diary entry for the given month and day
    diary = get_diary(config=config)
    diary_date = diary[
        (diary["date"].dt.day == date.day)
        & (diary["date"].dt.month == date.month)
        & (diary["date"].dt.year != date.year)
    ]
    return diary_date


def process_new_text(update: Update, context: CallbackContext, config):
    """Process the new text from the user."""
    # process the new text from the user
    # create a new diary entry
    chat_id = update.message.chat_id
    text = str(update.message.text)
    if correct_chat(chat_id, config) and len(text) > 0:
        logger.info(f"New text received: {text}")
        df = create_diary_entry(text)
        # get the diary
        diary = get_diary(config)
        # check if there is already an entry for today
        today = datetime.now().date()
        diary_today = diary[diary["date"].dt.date == today]
        diary = diary[diary["date"].dt.date != today]
        if len(diary_today) > 0:
            # if there is already an entry for today, append the new text to the existing entry
            # strftime() is used to convert the datetime object to a string
            logger.info(f"Entry for today already exists: {diary_today}")
            # check if last entry is older than 5 minutes
            last_date = diary_today["date"].values[-1]
            if pd.to_datetime(last_date) > (datetime.now() - timedelta(seconds=300)):
                logger.info("Last entry is less than 5 minutes old")
                df = create_diary_entry(text, insert_time=False)
            diary_today["entry"] = (
                diary_today["entry"].values[0] + f"\n" + df["entry"].values[0]
            )
            diary_today["images"] = [
                diary_today["images"].values[0] + df["images"].values[0]
            ]
            diary_today["date"] = df["date"].values[0]
            df = diary_today

        # append the new entry to the diary
        diary = pd.concat([diary, df])
        # save the diary
        diary.to_csv(config.get("diary_csv"), index=False)
        context.bot.send_message(chat_id=chat_id, text="Your entry has been saved.")
        return diary


def process_new_photo(update: Update, context: CallbackContext, config):

    if correct_chat(update.message.chat_id, config=config):
        # process the new photo from the user
        # get the diary
        diary = get_diary(config)
        # check if there is already an entry for today
        today = datetime.now().date()
        diary_today = diary[diary["date"].dt.date == today]
        diary = diary[diary["date"].dt.date != today]
        file_id = update.message.photo[-1].file_id
        if len(diary_today) > 0:
            # if there is already an entry for today, append the new photo to the existing entry
            logger.info(f"Entry for today already exists: {diary_today}")
            diary_today["images"] = [
                diary_today["images"].values[0] + [file_id + ".jpeg"]
            ]
            df = diary_today
        else:
            # if there is no entry for today, create a new entry
            logger.info("No entry for today exists")
            df = create_diary_entry("")
            df["images"] = [[file_id + ".jpeg"]]
        # save image to disk
        image = context.bot.get_file(file_id)
        image.download(Path(config.get("image_dir")) / Path(file_id + ".jpeg"))
        # append the new entry to the diary
        diary = pd.concat([diary, df])
        # save the diary
        diary.to_csv(config.get("diary_csv"), index=False)
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Your photo has been saved."
        )


def correct_chat(chat_id, config):
    logger.info(chat_id)
    check = int(config.get("chat_id")) == chat_id
    logger.info(f"Correct chat: {check}")
    return check
