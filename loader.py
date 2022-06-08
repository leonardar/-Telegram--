from aiogram import Bot, Dispatcher

from data import BOT_TOKEN, PROJECT, cache, credentials
from utils import db

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot, storage=cache)
db_manager = db.DBManager(credentials, PROJECT)
