from aiogram import F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from main import DP
from src.callback_data import RegistrationCallBackData
# from src.config import DP
from src.keyboards import menu_choice


@DP.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Приветствую! Для старта введите /menu"
    )


@DP.message(Command("menu"))
async def display_menu(message: Message) -> None:
    await message.answer(text="Выберите действие", reply_markup=menu_choice)


@DP.callback_query(RegistrationCallBackData.filter(F.button_name == "registration"))
async def choosing_france(call: CallbackQuery, callback_data: RegistrationCallBackData, state: FSMContext) -> None:
    await call.message.answer("В какой город Вы хотите полететь?", reply_markup=menu_choice)
