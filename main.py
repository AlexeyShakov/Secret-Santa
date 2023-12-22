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
        BotCommand(command="/manage_profile", description="Управление профилем"),
        BotCommand(command="/manage_game_as_player", description="Взаимодействие с игрой как пользователь"),
        BotCommand(command="/manage_game_as_creator", description="Взаимодействие с игрой как создатель"),
        BotCommand(command="/add_review", description="Оставить отзыв о боте"),
    ]
    await BOT.set_my_commands(bot_commands)


async def main() -> None:
    DP.include_routers(general_router, creator_game_router, player_router, user_profile_router)

    await setup_bot_commands()
    await DP.start_polling(BOT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
