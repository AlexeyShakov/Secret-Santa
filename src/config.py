import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TG_BOT_TOKEN")

BOT = Bot(TOKEN, parse_mode=ParseMode.HTML)
DP = Dispatcher()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")

MIN_PLAYERS = 3
