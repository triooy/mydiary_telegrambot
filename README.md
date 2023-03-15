# Diary Telegram Bot
With this repository you can start a telegram bot, which can be used to keep notes or diary entries.

## Install
1. Create a bot with [botfather](https://core.telegram.org/bots/tutorial)
2. Add your bot token to the `config.json` file
3. Create an openai api key and add it to the `config.json` file
4. Create a chat group with your bot and add the chat id to the `config.json` file
5. Give all rights to the bot in telegram
6. Checkout the repository and start with docker-compose

## Features
- Add entries
- Search for entries by date 
- Search for entries by text 
- Get similar entries
- Add photos to your entries
- Get a random entry
- Get a entry every day at a specific time for what you did in the past on this day
- Get your data as zip file
- Create a pdf version of your data for a specific time period
- Get statistical plots of your data
  
### Commands
- `/help` - Show all commands
![](./data/help.jpg)