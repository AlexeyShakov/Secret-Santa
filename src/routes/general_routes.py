from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from sqlalchemy import select

from src.db.db_connection import async_session_maker
from src.db.models import Player, Review
from src.filters import CancelFilter
from src.keyboards import data_to_write
from src.states import AddReviewState
from src.utils import get_obj

general_router = Router()


@general_router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Приветствую, {hbold(message.from_user.full_name)}!")


@general_router.message(Command("help"))
async def help(message: Message) -> None:
    info = "Данный бот предназначен для игры в тайногу Санту.\n\n" \
           "Для того, чтобы пользоваться ботом нужно зарегистрироваться. Для этого нужно вызвать /manage_profile и далее " \
           "нажать на соответствующую кнопку.\n\n" \
           "Далее Вы можете создать свою собственную игру и пригласить туда друзей, либо присоединиться к существующей " \
           "игре. Главным аттрибутом игры является ее уникальный идентификатор. Этот идентификатор создатель игры получает " \
           "после ее создания. После этого создатель должен передать этот идентификатор своим друзьям, чтобы они " \
           "присоединились к игре. При создании игры нужно задать количество участников, включая создателя! Как только " \
           "все игроки присоединятся, создателю придет сообщение.\n\n" \
           "Для ознакомления со всеми функциями бота нажмите на кнопку меню.\n\n" \
           "Счастливого нового года!"
    await message.answer(info)


@general_router.message(CancelFilter("Отменить"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()


@general_router.message(Command("add_review"))
async def add_review(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddReviewState.review)
    await message.answer("Напишите Ваш отзыв. В нем Вы можете написать, как о вещах, которые Вам понравились/не понравились, "\
    "или написать о вещах, которые можно улучшить", reply_markup=data_to_write)

@general_router.message(AddReviewState.review)
async def enter_review(message: Message, state: FSMContext) -> None:
    text = message.text
    if not text:
        await message.answer("Вы ввели пустое сообщение, это недопустимо. Введите еще раз", reply_markup=data_to_write)
        await state.clear()
        return
    async with async_session_maker() as session:
        current_user_chat_id = message.chat.id
        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)
        review = Review(text=text, review_creator=player)
        session.add(review)
        await state.clear()
        await session.commit()
        await message.answer("Отзыв успешно добавлен")
