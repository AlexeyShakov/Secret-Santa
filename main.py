import asyncio
import logging
import sys
from uuid import uuid4

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.utils.markdown import hbold

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from src.callback_data import RegistrationCallBackData, GameManageCallBackData, CreationCallBackData, \
    JoinGameCallBackData, StartGameCallBack
from src.config import TOKEN, MIN_PLAYERS
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


@dp.message(Command("help"))
async def help(message: Message) -> None:
    info = "Данный бот предназначен для игры в тайногу Санту.\n\n" \
           "Для того, чтобы пользоваться ботом нужно зарегистрироваться здесь /register.\n\n" \
           "Далее Вы можете создать свою собственную игру и пригласить туда друзей, либо присоединиться к существующей " \
           "игре.\n\n" \
           "Вы можете создать свою собственную игру здесь /create_game. Для этого " \
           "нужно ввести количество людей, кто будет играть, включая Вас. После того, как Вы введете число, Вы получите " \
           "уникальный идентификатор игры, который Вы должны передать всем участникам. Ваши друзья должны присоединиться " \
           "к игре здесь /join_game. После того, как все Ваши друзья присоединяться, Вам как создателю игры придет " \
           "сообщение. Далее введите команду /start_game и ждите результатов игры!\n\nЕсли Вы хотите присоединиться к " \
           "уже созданной кем-то игре, то просто введите /join_game и следуйте инструкции\n\n" \
           "Счастливого нового года!"
    # TODO добавить информацию об изменении игры
    # TODO добавить информацию об удалении игры
    await message.answer(info)


# @dp.message(Command("menu"))
# async def display_menu(message: Message) -> None:
#     await message.answer(text="Выберите действие", reply_markup=menu_choice)


#############REGISTRATION##############
# @dp.callback_query(RegistrationCallBackData.filter(F.button_name == "registration"))
@dp.message(Command("register"))
async def register(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationState.name)
    await message.answer(text="Введите свое имя", reply_markup=data_to_write)


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
        await message.answer(text="Вы уже зарегистрированы. Для дальнейших действий перейдите в меню")
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при регистрации пользователя: {e}")
    else:
        await message.answer(text="Вы успешно зарегистрировались! Введите /manage_game для дальнейших действий")


#############MANAGE_GAME##############
# @dp.callback_query(GameManageCallBackData.filter(F.button_name == "manage_game"))
# async def manage_game(call: CallbackQuery, callback_data: GameManageCallBackData) -> None:
#     await call.message.answer("Выбирайте", reply_markup=manage_game_choice)


#############CREATE_GAME##############
@dp.message(Command("create_game"))
async def create_game_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(CreationGameState.player_number)
    await message.answer("Введите количество участников", reply_markup=data_to_write)


@dp.message(CreationGameState.player_number)
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


#############JOIN_GAME##############
@dp.message(Command("join_game"))
async def join_game(message: Message, state: FSMContext) -> None:
    await state.set_state(JoinGameState.game_name)
    await message.answer("Введите индетификатор игры", reply_markup=data_to_write)


@dp.message(JoinGameState.game_name)
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

        current_user_chat_id = message.chat.id
        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)
        if not player:
            await message.answer(
                "Прежде чем присоединяться к игре, Вы должны зарегистрироваться. Выберите регистрацию в /menu")
            return

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
            await add_player_to_game(player=player, game=game, session=session, bot=bot)
            await message.answer("Вы успешно присоединились к игре.")
        except PlayerAlreadyAddedToGameException as e:
            await message.answer("Вы уже состоите в данной игре!")
        finally:
            await state.clear()


#############START_GAME##############
@dp.message(Command("start_game"))
async def start_game_handler(message: Message, state: FSMContext):
    await state.set_state(StartGameState.game_name)
    await message.answer("Введите индетификатор игры", reply_markup=data_to_write)


@dp.message(StartGameState.game_name)
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
            await bot.send_message(chat_id=santa.chat_id, text=message)
        await session.commit()


async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/help", description="Узнать информацию о боте"),
        BotCommand(command="/register", description="Зарегистрироваться"),
        BotCommand(command="/create_game", description="Создать игру"),
        BotCommand(command="/start_game", description="Запустить игру"),
        BotCommand(command="/join_game", description="Присоединиться к игре"),
        # TODO удалить игру
        # TODO изменить игру - изменить количество участников или активировать игру заново
    ]
    await bot.set_my_commands(bot_commands)


async def main() -> None:
    # bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await setup_bot_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
