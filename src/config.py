import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(os.path.abspath(__file__)).parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))


TOKEN = os.getenv("TG_BOT_TOKEN")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")

MIN_PLAYERS = 3
