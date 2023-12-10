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
           "игре. Главным аттрибутом игры является ее уникальный идентификатор. Этот идентификатор создатель игры получает" \
           "после ее создания. После этого создатель должен передать этот идентификатор своим друзьям, чтобы они " \
           "присоединились к игре. При создании игры нужно задать количество участников, включая создателя! Как только " \
           "все игроки присоединятся, создателю придет сообщение.\n\n" \
           "Для ознакомления со всеми функциями бота нажмите на кнопку меню.\n\n" \
           "Счастливого нового года!"
    # TODO добавить информацию об изменении игры
    # TODO добавить информацию об удалении игры
    await message.answer(info)
