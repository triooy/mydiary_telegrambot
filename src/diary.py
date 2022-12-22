from datetime import datetime
import pandas as pd
from telegram.ext import CallbackContext
from telegram import Update
import logging
import ast
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

def create_diary_entry(text):
    """Create a new diary entry for the user with the given text."""
    # create a new diary entry
    # get current date
    date = datetime.now()
    df = pd.DataFrame({'date': [date], 'entry': [text], 'images': [[]]})
    logger.info(f"New diary entry created: {df}")
    return df

def get_diary(config):
    """Get the diary of the user."""
    # get the diary of the user
    df = pd.read_csv(config.get('diary_csv'))
    df['images'] = df['images'].apply(ast.literal_eval)
    df['date'] = pd.to_datetime(df['date'])
    return df

def process_new_text(update: Update, context: CallbackContext, config):
    """Process the new text from the user."""
    # process the new text from the user
    # create a new diary entry
    chat_id = update.message.chat_id
    if correct_chat(chat_id, config):    
        text = str(update.message.text)
        logger.info(f"New text received: {text}")
        df = create_diary_entry(text)
        # get the diary
        diary = get_diary(config)
        # check if there is already an entry for today
        today = datetime.now().date()
        diary_today = diary[diary['date'].dt.date == today]
        diary = diary[diary['date'].dt.date != today]
        if len(diary_today) > 0:
            # if there is already an entry for today, append the new text to the existing entry
            # strftime() is used to convert the datetime object to a string
            logger.info(f"Entry for today already exists: {diary_today}")
            today = datetime.now().strftime('%d.%m.%Y %H:%M')
            diary_today['entry'] = diary_today['entry'].values[0] + f"\n\n{today}\n" + df['entry'].values[0]
            diary_today['images'] = [diary_today['images'].values[0] + df['images'].values[0]]
            df = diary_today
        
        # append the new entry to the diary
        diary = pd.concat([diary, df])
        # save the diary
        diary.to_csv(config.get('diary_csv'), index=False)
        return diary


def correct_chat(chat_id, config):
    logger.info(chat_id)
    return int(config.get("chat_id")) == chat_id

