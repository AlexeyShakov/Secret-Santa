

import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from src.config import TOKEN
from src.keyboards import menu_choice


# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Приветствую, {hbold(message.from_user.full_name)}!. Введите /menu для выбора действия")


@dp.message(Command("menu"))
async def display_menu(message: Message) -> None:
    await message.answer(text="Выберите действие", reply_markup=menu_choice)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
