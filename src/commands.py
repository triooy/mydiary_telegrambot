from telegram.ext import CallbackContext
from telegram import Update
import pytz
from datetime import time, timezone, datetime
from functools import partial
import random
from pathlib import Path
from diary import correct_chat, get_entry_by_date, get_diary

def daily(update: Update, context: CallbackContext, config):
    chat_id = update.message.chat_id
    if correct_chat(chat_id, config):
        context.job_queue.run_daily(
                partial(daily_job, config=config),
                time(hour=8, minute=30, tzinfo=pytz.timezone("Europe/Amsterdam")),
                context=chat_id,
                name=str(chat_id),
        )
        context.bot.send_message(chat_id=chat_id, text="Daily memory set!")

def daily_job(context: CallbackContext, config) -> None:
    job = context.job
    today = datetime.now().date()
    diary_today = get_entry_by_date(today, config)
    if len(diary_today) > 0:
        if len(diary_today) == 1:
            entry = diary_today
        else:
            # if there are multiple entries for today choose one
            entry = diary_today.sample()   
    text = entry['entry'].values[0]
    pretext = f"Here is what you wrote in {entry['date'].dt.date.values[0]}:\n\n"
    text = pretext + text
    images = entry['images'].values[0]
    context.bot.send_message(job.context, text=text)
    if len(images) > 0:
        # choose one image
        image = random.choice(images)
        with open(Path(config.get('image_dir')) / Path(image), 'rb') as f:   
            context.bot.send_photo(job.context, photo=f)
        
def get_random_entry(update: Update, context: CallbackContext, config):
    chat_id = update.message.chat_id
    if correct_chat(chat_id, config):
        diary = get_diary(config)
        random_entry = diary.sample()
        intro = f"Here is a random entry from {random_entry['date'].dt.date.values[0]}:\n\n"
        text = intro + str(random_entry['entry'].values[0])
        context.bot.send_message(chat_id=chat_id, text=text)
        images = random_entry['images'].values[0]
        if len(images) > 0:
            for image in images:
                with open(Path(config.get('image_dir')) / Path(image), 'rb') as f:   
                    context.bot.send_photo(chat_id=chat_id, photo=f)
        
def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True