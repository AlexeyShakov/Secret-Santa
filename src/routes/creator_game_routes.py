import logging
from uuid import uuid4

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from sqlalchemy import select

from main import BOT
from src.config import MIN_PLAYERS
from src.db.db_connection import async_session_maker
from src.db.models import Game
from src.keyboards import data_to_write
from src.states import CreationGameState, StartGameState, DeleteGameState, DisplayConnectedPlayersState, \
    ChangePlayersNumberState
from src.utils import create_game, get_obj, find_matches

creator_game_router = Router()


@creator_game_router.message(Command("create_game"))
async def create_game_handler(message: Message, state: FSMContext) -> None:
    # Там может что-то оказаться, если юзер ввел эту команду, потом ввел другую и потом нажал на первоначальную команду
    # Лучше очищать state перед каждым использованием
    await state.clear()
    await state.set_state(CreationGameState.player_number)
    await message.answer("Введите количество участников", reply_markup=data_to_write)


@creator_game_router.message(CreationGameState.player_number)
async def write_number_of_player(message: Message, state: FSMContext) -> None:
    try:
        number_of_player = int(message.text)
    except Exception as e:
        logging.exception(f"Неверное число: {e}")
        await message.answer("Введите число", reply_markup=data_to_write)
    else:
        if number_of_player < MIN_PLAYERS:
            await message.answer(
                f"Количество игроков должно быть больше {MIN_PLAYERS}! Введите количество игроков еще раз",
                reply_markup=data_to_write)
            return
        await state.clear()
        name = str(uuid4())[:10]
        await create_game(name=name, creator_chat_id=message.chat.id, number_of_player=number_of_player)
        await message.answer(f"Индефикатор Вашей игры: {hbold(name)}")


@creator_game_router.message(Command("start_game"))
async def start_game_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StartGameState.game_name)
    await message.answer("Введите индетификатор игры", reply_markup=data_to_write)


@creator_game_router.message(StartGameState.game_name)
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


@creator_game_router.message(Command("delete_game"))
async def delete_game_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(DeleteGameState.game_name)
    await message.answer("Введите идентификтор игры")


@creator_game_router.message(DeleteGameState.game_name)
async def enter_game_name_for_deleting(message: Message, state: FSMContext):
    game_name = message.text
    async with async_session_maker() as session:
        game_query = select(Game).filter_by(name=game_name)
        game: Game = await get_obj(game_query, session)
        if not game:
            await message.answer("Игра с таким идентификатором не существует!")
            return
        if game.creator.chat_id != message.chat.id:
            await message.answer("Только создатель может удалить игру!")
            return
        await state.clear()
        await session.delete(game)
        await session.commit()
        await message.answer("Успешно завершено!")


@creator_game_router.message(Command("display_connected_players"))
async def display_connected_players(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(DisplayConnectedPlayersState.game_name)
    await message.answer("Введите идентификтор игры")


@creator_game_router.message(DisplayConnectedPlayersState.game_name)
async def display_players(message: Message, state: FSMContext):
    game_name = message.text
    async with async_session_maker() as session:
        game_query = select(Game).filter_by(name=game_name)
        game: Game = await get_obj(game_query, session)
        if not game:
            await message.answer("Игра с таким идентификатором не существует!")
            return
        if game.creator.chat_id != message.chat.id:
            await message.answer("Только создатель может просматривать участников!")
            return
        await state.clear()
        game_players = [f"{player.name} {player.last_name}" for player in game.players]
        if game_players:
            await message.answer("\n".join(game_players))
        else:
            await message.answer("К игре еще никто не присоединился!")


@creator_game_router.message(Command("change_players_number"))
async def change_players_number(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ChangePlayersNumberState.game_name)
    await message.answer("Введите идентификтор игры")


@creator_game_router.message(ChangePlayersNumberState.game_name)
async def enter_new_players_number(message: Message, state: FSMContext):
    game_name = message.text
    async with async_session_maker() as session:
        game_query = select(Game).filter_by(name=game_name)
        game: Game = await get_obj(game_query, session)
        if not game:
            await message.answer("Игра с таким идентификатором не существует!")
            return
        if game.creator.chat_id != message.chat.id:
            await message.answer("Только создатель может поменять количество участников!")
            return
        await state.update_data(game_name=game.name)
        await state.set_state(ChangePlayersNumberState.new_players_number)
        await message.answer("Введите новое количество участников", reply_markup=data_to_write)


@creator_game_router.message(ChangePlayersNumberState.new_players_number)
async def enter_new_players_number(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        new_number_of_players = int(message.text)
    except Exception:
        await message.answer("Вы ввели неверное число. Введите заново", reply_markup=data_to_write)
        return
    await state.clear()
    async with async_session_maker() as session:
        game_query = select(Game).filter_by(name=data["game_name"])
        game: Game = await get_obj(game_query, session)
        if not game:
            await message.answer("Игра с таким идентификатором не существует!")
            return
        game.number_of_player = new_number_of_players
        await session.commit()
        await message.answer("Успешно завершено!")
