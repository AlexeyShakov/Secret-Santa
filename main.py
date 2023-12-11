import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from src.config import TOKEN
from src.routes import *

DP = Dispatcher()
BOT = Bot(TOKEN, parse_mode=ParseMode.HTML)


async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/help", description="Узнать информацию о боте"),
        BotCommand(command="/register", description="Зарегистрироваться"),
        BotCommand(command="/delete_profile", description="Удалить профиль"),
        BotCommand(command="/create_game", description="Создать игру"),
        BotCommand(command="/start_game", description="Запустить игру"),
        BotCommand(command="/join_game", description="Присоединиться к игре"),
        BotCommand(command="/change_name", description="Поменять имя"),
        BotCommand(command="/change_last_name", description="Поменять фамилию"),
        BotCommand(command="/display_connected_players", description="Просмотреть присоединившихся игроков"),
        BotCommand(command="/delete_game", description="Удалить игру"),
        BotCommand(command="/change_players_number", description="Изменить количество участников"),
        BotCommand(command="/leave_game", description="Покинуть игру"),
    ]
    await BOT.set_my_commands(bot_commands)


async def main() -> None:
    DP.include_routers(general_router, creator_game_router, player_router, user_profile_router)

    await setup_bot_commands()
    await DP.start_polling(BOT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
