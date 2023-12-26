import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold
from sqlalchemy import select

from main import BOT
from src.callback_data import JoinGameCallBackData, LeaveGameCallBackData
from src.db.db_connection import async_session_maker
from src.db.models import Game, Player
from src.exceptions import PlayerAlreadyAddedToGameException
from src.keyboards import data_to_write
from src.keyboards.player import player_keyboard
from src.states import JoinGameState, LeaveGameState
from src.utils import get_obj, add_player_to_game


player_router = Router()


@player_router.message(Command("manage_game_as_player"))
async def manage_game_as_player(message: Message) -> None:
    await message.answer(text="Выберите действие", reply_markup=player_keyboard)


@player_router.callback_query(JoinGameCallBackData.filter(F.button_name == "join_game"))
async def join_game(call: CallbackQuery, callback_data: JoinGameCallBackData, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(JoinGameState.game_name)
    await call.message.answer("Введите индетификатор игры", reply_markup=data_to_write)


@player_router.message(JoinGameState.game_name)
async def write_id_for_joining(message: Message, state: FSMContext) -> None:
    async with async_session_maker() as session:
        game_name = message.text
        game_query = select(Game).filter_by(name=game_name)
        game = await get_obj(game_query, session)

        if not game:
            await message.answer("Вы ввели не существующий идентификатор игры. Повторите попытку",
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
                "Прежде чем присоединяться к игре, Вы должны зарегистрироваться. Выберите комманду регистрации в menu")
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


@player_router.callback_query(LeaveGameCallBackData.filter(F.button_name == "leave_game"))
async def leave_game(call: CallbackQuery, callback_data: LeaveGameCallBackData, state: FSMContext):
    await state.clear()
    async with async_session_maker() as session:
        current_user_chat_id = call.message.chat.id
        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)
        if not player:
            await call.message.answer(
                "Вы должны зарегистрироваться прежде чем выполнить это действие!")
            return
    await state.set_state(LeaveGameState.game_name)
    await call.message.answer("Введите индетификатор игры", reply_markup=data_to_write)


@player_router.message(LeaveGameState.game_name)
async def enter_game_id_for_leaving(message: Message, state: FSMContext):
    async with async_session_maker() as session:
        game_query = select(Game).filter_by(name=message.text)
        game: Game = await get_obj(game_query, session)
        if not game:
            await message.answer("Вы ввели не существующий идентификатор игры. Повторите попытку",
                                 reply_markup=data_to_write)
            await state.clear()
            return
        current_user_chat_id = message.chat.id
        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)
        game.players.remove(player)
        await session.commit()
        await message.answer("Успешно завершено!")
        await state.clear()
