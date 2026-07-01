from aiogram import Bot, Dispatcher

from app.config import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
