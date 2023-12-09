import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from sqlalchemy import select

from main import BOT
from src.db.db_connection import async_session_maker
from src.db.models import Game, Player
from src.exceptions import PlayerAlreadyAddedToGameException
from src.keyboards import data_to_write
from src.states import JoinGameState
from src.utils import get_obj, add_player_to_game

join_game_router = Router()

@join_game_router.message(Command("join_game"))
async def join_game(message: Message, state: FSMContext) -> None:
    await state.set_state(JoinGameState.game_name)
    await message.answer("Введите индетификатор игры", reply_markup=data_to_write)


@join_game_router.message(JoinGameState.game_name)
async def write_id_for_joining(message: Message, state: FSMContext) -> None:
    async with async_session_maker() as session:
        game_name = message.text
        game_query = select(Game).filter_by(name=game_name)
        game = await get_obj(game_query, session)


        if not game:
            await message.answer("Вы ввели не существующее название игры. Повторите попытку",
                                 reply_markup=data_to_write)
            await state.clear()
            return
        if len(game.players) + 1 == game.number_of_player:
            await message.answer("К данной игре присоединилось достаточное количество игроков!")
            await state.clear()
            return
        current_user_chat_id = message.chat.id
        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)
        if not player:
            await message.answer(
                "Прежде чем присоединяться к игре, Вы должны зарегистрироваться. Выберите регистрацию в /menu")
            return
        logging.info(f"Игрок {player.name} {player.last_name} пытается присоединиться к игре {hbold(game.name)}")

        if game.creator.chat_id == current_user_chat_id:
            await state.clear()
            await message.answer("Вы уже состоите в данной игре как создатель!")
            return

        game_players_ids = [player.chat_id for player in game.players]
        if player.chat_id in game_players_ids:
            await message.answer("Вы уже присоединились к игре!")
            await state.clear()
            return

        try:
            await add_player_to_game(player=player, game=game, session=session, bot=BOT)
            # TODO здесь можно засунуть эти две задачи asyncio.Task
            await message.answer("Вы успешно присоединились к игре.")
            await BOT.send_message(chat_id=game.creator.chat_id, text=f"{player.name} {player.last_name} "
                                                                      f"присоединился(ась) к игре {hbold(game.name)}")
            logging.info(f"Игрок {player.name} {player.last_name} успешно присоединился к игре {hbold(game.name)}")
        except PlayerAlreadyAddedToGameException as e:
            await message.answer("Вы уже состоите в данной игре!")
        finally:
            await state.clear()
