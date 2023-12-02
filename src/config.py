import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TG_BOT_TOKEN")

BOT = Bot(TOKEN, parse_mode=ParseMode.HTML)
DP = Dispatcher()
