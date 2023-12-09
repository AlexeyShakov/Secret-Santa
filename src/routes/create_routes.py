import logging
from uuid import uuid4

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from src.config import MIN_PLAYERS
from src.keyboards import data_to_write
from src.states import CreationGameState
from src.utils import create_game


create_router = Router()


@create_router.message(Command("create_game"))
async def create_game_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(CreationGameState.player_number)
    await message.answer("Введите количество участников", reply_markup=data_to_write)


@create_router.message(CreationGameState.player_number)
async def write_number_of_player(message: Message, state: FSMContext) -> None:
    try:
        number_of_player = int(message.text)
    except Exception as e:
        logging.exception(f"Неверное число: {e}")
        await message.answer("Введите число", reply_markup=data_to_write)
    else:
        if number_of_player < MIN_PLAYERS:
            await message.answer(f"Количество игроков должно быть больше {MIN_PLAYERS}! Введите количество игроков еще раз",
                                 reply_markup=data_to_write)
            return
        await state.clear()
        name = str(uuid4())[:10]
        await create_game(name=name, creator_chat_id=message.chat.id, number_of_player=number_of_player)
        await message.answer(f"Индефикатор Вашей игры: {hbold(name)}")
