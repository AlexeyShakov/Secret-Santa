from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError


import logging

from src.keyboards import data_to_write
from src.states import RegistrationState
from src.utils import register_player

registration_router = Router()


@registration_router.message(Command("register"))
async def register(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationState.name)
    await message.answer(text="Введите свое имя", reply_markup=data_to_write)


@registration_router.message(RegistrationState.name)
async def write_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(RegistrationState.last_name)
    await message.answer(text="Введите свою фамилию", reply_markup=data_to_write)


@registration_router.message(RegistrationState.last_name)
async def write_last_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    try:
        await register_player(
            name=data["name"],
            last_name=message.text,
            chat_id=message.chat.id
        )
    except IntegrityError as e:
        await message.answer(text="Вы уже зарегистрированы. Для дальнейших действий перейдите в меню")
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при регистрации пользователя: {e}")
    else:
        await message.answer(text="Вы успешно зарегистрировались! Для дальнейших действий нажмите на кнопку меню")
