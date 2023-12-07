import asyncio
import logging
import sys
from uuid import uuid4
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from src.callback_data import RegistrationCallBackData, GameManageCallBackData, CreationCallBackData, \
    JoinGameCallBackData, StartGameCallBack
from src.config import TOKEN
from src.db.db_connection import async_session_maker
from src.db.models import Game, Player
from src.exceptions import PlayerAlreadyAddedToGameException
from src.keyboards import menu_choice, manage_game_choice, data_to_write
from src.utils import register_player, create_game, get_obj, add_player_to_game, find_matches
from src.states import RegistrationState, CreationGameState, JoinGameState, StartGameState

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Приветствую, {hbold(message.from_user.full_name)}!")


@dp.message(Command("menu"))
async def display_menu(message: Message) -> None:
    await message.answer(text="Выберите действие", reply_markup=menu_choice)


#############REGISTRATION##############
@dp.callback_query(RegistrationCallBackData.filter(F.button_name == "registration"))
async def register(call: CallbackQuery, callback_data: RegistrationCallBackData, state: FSMContext) -> None:
    await state.set_state(RegistrationState.name)
    await call.message.answer(text="Введите свое имя", reply_markup=data_to_write)


@dp.message(RegistrationState.name)
async def write_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(RegistrationState.last_name)
    await message.answer(text="Введите свою фамилию", reply_markup=data_to_write)


@dp.message(RegistrationState.last_name)
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
        await message.answer(text="Вы уже зарегистрированы. Для дальнейших действий перейдите в /menu")
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при регистрации пользователя: {e}")
    else:
        await message.answer(text="Вы успешно зарегистрировались! Введите /manage_game для дальнейших действий")


#############MANAGE_GAME##############
@dp.callback_query(GameManageCallBackData.filter(F.button_name == "manage_game"))
async def manage_game(call: CallbackQuery, callback_data: GameManageCallBackData) -> None:
    await call.message.answer("Выбирайте", reply_markup=manage_game_choice)


#############CREATE_GAME##############
@dp.callback_query(CreationCallBackData.filter(F.button_name == "create_game"))
async def create_game_handler(call: CallbackQuery, callback_data: CreationCallBackData, state: FSMContext) -> None:
    await state.set_state(CreationGameState.player_number)
    await call.message.answer("Введите количество участников", reply_markup=data_to_write)


@dp.message(CreationGameState.player_number)
async def write_number_of_player(message: Message, state: FSMContext) -> None:
    try:
        number_of_player = int(message.text)
    except Exception as e:
        logging.exception(f"Неверное число: {e}")
        await message.answer("Введите число", reply_markup=data_to_write)
    else:
        if number_of_player < 2:
            await message.answer("Количество игроков должно быть больше 2! Введите количество игроков еще раз",
                                 reply_markup=data_to_write)
        await state.clear()
        name = str(uuid4())[:10]
        await create_game(name=name, creator_chat_id=message.chat.id, number_of_player=number_of_player)
        await message.answer(f"Индефикатор Вашей игры: {hbold(name)}")


#############JOIN_GAME##############
@dp.callback_query(JoinGameCallBackData.filter(F.button_name == "join_game"))
async def join_game(call: CallbackQuery, callback_data: JoinGameCallBackData, state: FSMContext) -> None:
    await state.set_state(JoinGameState.game_name)
    await call.message.answer("Введите индетификатор игры", reply_markup=data_to_write)


@dp.message(JoinGameState.game_name)
async def write_id_for_joining(message: Message, state: FSMContext) -> None:
    async with async_session_maker() as session:
        game_name = message.text
        game_query = select(Game).filter_by(name=game_name)
        game = await get_obj(game_query, session)

        current_user_chat_id = message.chat.id
        if game.creator.chat_id == current_user_chat_id:
            await state.clear()
            await message.answer("Вы уже состоите в данной игре как создатель!")

        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)
        if not player:
            await message.answer(
                "Прежде чем присоединяться к игре, Вы должны зарегистрироваться. Выберите регистрацию в /menu")

        if not game:
            await message.answer("Вы ввели не существующее название игры. Повторите попытку",
                                 reply_markup=data_to_write)
            return
        await state.clear()
        try:
            await add_player_to_game(player=player, game=game, session=session)
            await message.answer("Вы успешно присоединились к игре.")
        except PlayerAlreadyAddedToGameException as e:
            await message.answer("Вы уже состоите в данной игре!")


#############START_GAME##############
@dp.callback_query(StartGameCallBack.filter(F.button_name == "start_game"))
async def start_game_handler(call: CallbackQuery, callback_data: StartGameCallBack, state: FSMContext):
    await state.set_state(StartGameState.game_name)
    await call.message.answer("Введите индетификатор игры", reply_markup=data_to_write)


@dp.message(StartGameState.game_name)
async def write_game_name_for_starting(message: Message, state: FSMContext) -> None:
    game_name = message.text
    async with async_session_maker() as session:
        game_query = select(Game).filter_by(name=game_name)
        game: Game = await get_obj(game_query, session)

        if not game.is_active:
            await message.answer("Данная игра уже завершилась!")
        if game.creator.chat_id != message.chat.id:
            await message.answer("Только создатель может начать игру!")
        if game.number_of_player != len(game.players):
            await message.answer("Не все игроки еще присоединились к игре!")

        matches = await find_matches(game)
        await state.clear()
        # TODO Засунуть в asyncio.Tasks?
        for santa, gift_taker in matches.items():
            message = f"Вы должны сделать подарок пользователю {hbold(gift_taker.name)} {hbold(gift_taker.last_name)}"
            await bot.send_message(chat_id=santa.chat_id, text=message)
        game.is_active = False
        await session.commit()


async def main() -> None:
    # bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
