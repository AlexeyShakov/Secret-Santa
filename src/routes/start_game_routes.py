from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from sqlalchemy import select

from main import BOT
from src.db.db_connection import async_session_maker
from src.db.models import Game
from src.keyboards import data_to_write
from src.states import StartGameState
from src.utils import find_matches, get_obj

start_game_router = Router()


@start_game_router.message(Command("start_game"))
async def start_game_handler(message: Message, state: FSMContext):
    await state.set_state(StartGameState.game_name)
    await message.answer("Введите индетификатор игры", reply_markup=data_to_write)


@start_game_router.message(StartGameState.game_name)
async def write_game_name_for_starting(message: Message, state: FSMContext) -> None:
    game_name = message.text
    async with async_session_maker() as session:
        game_query = select(Game).filter_by(name=game_name)
        game: Game = await get_obj(game_query, session)
        if not game:
            await message.answer("Игра с таким идентификатором не существует!")
            return
        if not game.is_active:
            await message.answer("Данная игра уже завершилась!")
            return
        if game.creator.chat_id != message.chat.id:
            await message.answer("Только создатель может начать игру!")
            return
        # +1 потому что еще есть создатель игры!
        if game.number_of_player != len(game.players) + 1:
            await message.answer("Не все игроки еще присоединились к игре!")
            return
        matches = await find_matches(game, session)
        await state.clear()
        # TODO Засунуть в asyncio.Tasks?
        for santa, gift_taker in matches.items():
            message = f"Вы должны сделать подарок пользователю {hbold(gift_taker.name)} {hbold(gift_taker.last_name)}"
            await BOT.send_message(chat_id=santa.chat_id, text=message)
        await session.commit()
