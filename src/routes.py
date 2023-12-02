from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from main import DP
# from src.config import DP
from src.keyboards import menu_choice


@DP.message(CommandStart())
async def start(message: Message) -> None:
    print("Я ТУТ")
    await message.answer(
        "Приветствую! Для старта введите /menu"
    )


@DP.message(Command("menu"))
async def display_menu(message: Message) -> None:
    await message.answer(text="Выберите действие", reply_markup=menu_choice)
