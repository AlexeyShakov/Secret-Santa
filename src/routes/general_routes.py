from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold


general_router = Router()


@general_router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Приветствую, {hbold(message.from_user.full_name)}!")


@general_router.message(Command("help"))
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
