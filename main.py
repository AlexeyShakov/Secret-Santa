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
    JoinGameCallBackData
from src.config import TOKEN
from src.db.db_connection import async_session_maker
from src.db.models import Game, Player
from src.exceptions import PlayerAlreadyAddedToGameException
from src.keyboards import menu_choice, manage_game_choice, data_to_write
from src.utils import register_player, create_game, get_obj, add_player_to_game
from src.states import RegistrationState, CreationGameState, JoinGameState

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Приветствую, {hbold(message.from_user.full_name)}!. Введите /menu для выбора действия")


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
        await message.answer(text="Вы уже зарегистрированы")
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при регистрации пользователя: {e}")
    else:
        await message.answer(text="Вы успешно зарегистрировались!")


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
async def write_number_of_player(message: Message, state: FSMContext) -> None:
    async with async_session_maker() as session:
        # TODO проверка, что пользователь не создатель
        # TODO получение пользователя и игры можно объединить в одну asyncio.Task, чтобы выиграть во времени
        game_name = message.text
        game_query = select(Game).filter_by(name=game_name)
        game = await get_obj(game_query, session)

        player_query = select(Player).filter_by(chat_id=message.chat.id)
        # TODO проверка на то, что пользователь зареганный. Сейчас может быть незареганный пользователь
        player = await get_obj(player_query, session)
        if not game:
            await message.answer("Вы ввели не существующее название игры. Повторите попытку", reply_markup=data_to_write)
            return
        await state.clear()
        try:
            await add_player_to_game(player=player, game=game, session=session)
            await message.answer("Вы успешно присоединились к игре")
        except PlayerAlreadyAddedToGameException as e:
            await message.answer("Вы уже состоите в данной игре!")





async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
