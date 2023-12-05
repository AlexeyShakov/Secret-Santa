import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from src.callback_data import RegistrationCallBackData, GameManageCallBackData
from src.config import TOKEN
from src.keyboards import menu_choice, manage_game_choice
from src.utils import register_player

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Приветствую, {hbold(message.from_user.full_name)}!. Введите /menu для выбора действия")


@dp.message(Command("menu"))
async def display_menu(message: Message) -> None:
    await message.answer(text="Выберите действие", reply_markup=menu_choice)


@dp.callback_query(RegistrationCallBackData.filter(F.button_name == "registration"))
async def register(call: CallbackQuery, callback_data: RegistrationCallBackData) -> None:
    await register_player(
        chat_id=call.message.chat.id,
        name="Алеша",
        last_name="Шаков"
    )
    await call.message.answer(text="Вы успешно зарегистрировались!")


@dp.callback_query(GameManageCallBackData.filter(F.button_name == "manage_game"))
async def manage_game(call: CallbackQuery, callback_data: GameManageCallBackData) -> None:
    await call.message.answer("Выбирайте", reply_markup=manage_game_choice)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
