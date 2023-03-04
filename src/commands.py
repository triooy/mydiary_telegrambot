import logging
import random
import shutil
from datetime import datetime, time, timezone
from functools import partial
from pathlib import Path

import plotly.express as px
import pytz
import telegram
from diary import correct_chat, get_diary, get_entry_by_date
from pdf import create_pdf
from telegram import Update
from telegram.ext import CallbackContext

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


async def help(update: Update, context: CallbackContext, config) -> None:
    chat_id = update.message.chat_id
    if correct_chat(chat_id, config):
        # sends a markup message with the commands
        text = """Hi! I'm your personal diary bot. I can help you keep a diary and remind you to write in it. 
        \n\nHere are the commands I understand:
        \n`/daily` - I will send you every day a diary entry created on this day in the past at 8:30.
        \n`/random` - I will send you a random entry from your diary
        \n`/get_data` - I will send you your diary as a csv file and your images zipped
        \n`/stats` - I will send you a plot of your entries per day
        \n`/pdf -s 19.01.2012 -e 22.12.2022` - I will send you a pdf of your diary
        \n`/help` - I will send you this message
        """
        await context.bot.send_message(
            chat_id=chat_id, text=text, parse_mode=telegram.constants.ParseMode.MARKDOWN
        )
        await delete_message(context, update.message.chat_id, update.message.message_id)


async def daily(update: Update, context: CallbackContext, config) -> None:
    chat_id = update.message.chat_id
    if correct_chat(chat_id, config):
        context.job_queue.run_daily(
            partial(daily_job, config=config),
            time(hour=8, minute=30, tzinfo=pytz.timezone("Europe/Amsterdam")),
            chat_id=chat_id,
            name=str(chat_id),
        )
        await context.bot.send_message(chat_id=chat_id, text="Daily memory set!")
        await delete_message(context, update.message.chat_id, update.message.message_id)


async def get_data(update: Update, context: CallbackContext, config) -> None:
    chat_id = update.message.chat_id
    if correct_chat(chat_id, config):
        # zip data send
        current_date = datetime.now().date()
        zip = shutil.make_archive(
            config.get("data_dir") + f"_{current_date}", "zip", config.get("data_dir")
        )
        await context.bot.send_document(chat_id=chat_id, document=open(zip, "rb"))
        await delete_message(context, update.message.chat_id, update.message.message_id)


async def daily_job(context: CallbackContext, config) -> None:
    today = datetime.now().date()
    diary_today = get_entry_by_date(today, config)
    if len(diary_today) > 0:
        if len(diary_today) == 1:
            entry = diary_today
        else:
            # if there are multiple entries for today choose one
            entry = diary_today.sample()
        text = entry["entry"].values[0]
        pretext = f"There are {len(diary_today)} entries for today. \nHere is what you wrote in {entry['date'].dt.date.values[0]}:\n\n"
        text = pretext + text
        images = entry["images"].values[0]
        await context.bot.send_message(context.job.chat_id, text=text)
        if len(images) > 0:
            # choose one image
            image = random.choice(images)
            with open(Path(config.get("image_dir")) / Path(image), "rb") as f:
                await context.bot.send_photo(context.job.chat_id, photo=f)
    else:
        logger.info("No entry for today")
        await context.bot.send_message(
            context.job.chat_id, text="No entry for today, you should write one!"
        )


async def delete_message(context: CallbackContext, chat_id, message_id):
    """Deletes the message that triggered the command.

    Args:
        context (CallbackContext): _description_
        chat_id (_type_): _description_
        message_id (_type_): _description_
    """
    await context.bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )


async def get_random_entry(update: Update, context: CallbackContext, config):
    """Creates a random entry from the diary and sends it to the user.

    Args:
        update (Update): _description_
        context (CallbackContext): _description_
        config (_type_): _description_
    """
    chat_id = update.message.chat_id
    if correct_chat(chat_id, config):
        diary = get_diary(config)
        random_entry = diary.sample()
        intro = (
            f"Here is a random entry from {random_entry['date'].dt.date.values[0]}:\n\n"
        )
        text = intro + str(random_entry["entry"].values[0])
        await context.bot.send_message(chat_id=chat_id, text=text)
        images = random_entry["images"].values[0]
        if len(images) > 0:
            for image in images:
                with open(Path(config.get("image_dir")) / Path(image), "rb") as f:
                    await context.bot.send_photo(chat_id=chat_id, photo=f)
        await delete_message(context, update.message.chat_id, update.message.message_id)


async def get_stats(update: Update, context: CallbackContext, config):
    """Generates a table with the number of entries per day and sends it to the user.

    Args:
        update (Update): _description_
        context (CallbackContext): _description_
        config (_type_): _description_
    """
    chat_id = update.message.chat_id
    if correct_chat(chat_id, config):
        diary = get_diary(config)
        word_count = diary["entry"].str.split().str.len().sum()
        entries = len(diary)
        mean_words = round(word_count / entries, 2)

        ## generate a historgram of the number of entries per day
        ## plot it with seaborn
        distrubution_over_weekdays = diary["date"].dt.day_name().value_counts()
        # sort the days of the week
        distrubution_over_weekdays = distrubution_over_weekdays.reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        )
        distrubution_over_weekdays = (
            distrubution_over_weekdays.to_frame()
            .reset_index()
            .rename(columns={"index": "weekday", "date": "entries"})
        )

        fig = px.bar(
            distrubution_over_weekdays,
            x="weekday",
            y="entries",
            title="Number of entries per weekday",
            color="entries",
            color_continuous_scale=px.colors.sequential.Sunsetdark,
            width=800,
            height=400,
            text="entries",
        )
        fig.write_image("/tmp/entries_per_weekday.png", format="png", engine="kaleido")

        # distribution over months
        distrubution_over_months = diary["date"].dt.month_name().value_counts()
        # sort the months
        distrubution_over_months = distrubution_over_months.reindex(
            [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
        )
        distrubution_over_months = (
            distrubution_over_months.to_frame()
            .reset_index()
            .rename(columns={"index": "month", "date": "entries"})
        )
        fig = px.bar(
            distrubution_over_months,
            x="month",
            y="entries",
            title="Number of entries per month",
            color="entries",
            color_continuous_scale=px.colors.sequential.Sunsetdark,
            width=800,
            height=400,
            text="entries",
        )
        fig.write_image("/tmp/entries_per_month.png", format="png", engine="kaleido")

        stats = f"Stats:\n\nNumber of entries: {entries}\nNumber of words: {word_count}\nMean words per entry: {mean_words}"

        await context.bot.send_message(chat_id=chat_id, text=stats)
        await context.bot.send_photo(
            chat_id=chat_id, photo=open("/tmp/entries_per_weekday.png", "rb")
        )
        await context.bot.send_photo(
            chat_id=chat_id, photo=open("/tmp/entries_per_month.png", "rb")
        )

        await delete_message(context, update.message.chat_id, update.message.message_id)


async def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = await context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        await job.schedule_removal()
    return True


async def pdf(update: Update, context: CallbackContext, config):

    chat_id = update.message.chat_id
    if correct_chat(chat_id, config):
        diary = get_diary(config)
        # read parameters from message -s for start_date and -e for end_date
        args = context.args
        start_date = None
        end_date = None
        if "-s" in args:
            start_date = args[args.index("-s") + 1]
        if "-e" in args:
            end_date = args[args.index("-e") + 1]
        pdf_path = create_pdf(diary, config["author"], start_date, end_date)
        await context.bot.send_document(chat_id=chat_id, document=open(pdf_path, "rb"))
        await delete_message(context, update.message.chat_id, update.message.message_id)
