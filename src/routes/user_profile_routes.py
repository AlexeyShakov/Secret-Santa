from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

import logging

from src.callback_data import RegistrationCallBackData, DeleteProfileCallBackData, ChangeNameCallBackData, \
    ChangeLastNameCallBackData, EditProfileCallBackData
from src.db.db_connection import async_session_maker
from src.db.models import Player, Game
from src.keyboards import data_to_write, manage_profile_keyboard, change_name_or_last_name_keyboard
from src.states import RegistrationState, DeleteProfileState, ChangeNameState, ChangeLastNameState
from src.utils import register_player, get_obj

user_profile_router = Router()


@user_profile_router.message(Command("manage_profile"))
async def manage_profile(message: Message) -> None:
    await message.answer(text="Выбирите действие", reply_markup=manage_profile_keyboard)


@user_profile_router.callback_query(RegistrationCallBackData.filter(F.button_name == "registration"))
async def choosing_register(call: CallbackQuery, callback_data: RegistrationCallBackData, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(RegistrationState.name)
    await call.message.answer(text="Введите свое имя", reply_markup=data_to_write)


@user_profile_router.message(RegistrationState.name)
async def write_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(RegistrationState.last_name)
    await message.answer(text="Введите свою фамилию", reply_markup=data_to_write)


@user_profile_router.message(RegistrationState.last_name)
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
        await message.answer(text="Вы успешно зарегистрировались! Для дальнейших действий нажмите на кнопку меню")


@user_profile_router.callback_query(DeleteProfileCallBackData.filter(F.button_name == "delete_profile"))
async def delete_profile(call: CallbackQuery, callback_data: DeleteProfileCallBackData, state: FSMContext) -> None:
    await state.clear()
    async with async_session_maker() as session:
        current_user_chat_id = call.message.chat.id
        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)
        if not player:
            await call.message.answer("У Вас нет профиля!")

        player_games_query = select(Game).filter_by(creator=player, is_active=True)
        player_games = await session.execute(player_games_query)
        result = player_games.scalars().all()
        if result:
            await state.set_state(DeleteProfileState.answer)
            await call.message.answer("У Вас есть активные игры, в которых Вы являетесь создателем. "
                                 f"Если Вы действительно хотите удалить профиль, то нажмите {hbold('да')}. "
                                 "Если нет, то введите любое слово", reply_markup=data_to_write)
        else:
            await session.delete(player)
            await session.commit()
            await call.message.answer("Вы успешно удалили профиль")


@user_profile_router.message(DeleteProfileState.answer)
async def write_answer(message: Message, state: FSMContext) -> None:
    answer = message.text
    if answer.lower() == "да":
        async with async_session_maker() as session:
            await state.clear()
            current_user_chat_id = message.chat.id
            player_query = select(Player).filter_by(chat_id=current_user_chat_id)
            player = await get_obj(player_query, session)

            await session.delete(player)
            await session.commit()
            await message.answer("Вы успешно удалили профиль")
    else:
        await state.clear()


@user_profile_router.callback_query(EditProfileCallBackData.filter(F.button_name == "edit_profile"))
async def edit_profile(call: CallbackQuery, callback_data: EditProfileCallBackData, state: FSMContext):
    await call.message.answer(text="Выбирете действие", reply_markup=change_name_or_last_name_keyboard)


@user_profile_router.callback_query(ChangeNameCallBackData.filter(F.button_name == "change_name"))
async def change_name(call: CallbackQuery, callback_data: ChangeNameCallBackData, state: FSMContext):
    await state.clear()
    async with async_session_maker() as session:
        current_user_chat_id = call.message.chat.id
        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)
        if not player:
            await call.message.answer("У Вас не профиля, Вы должны зарегистрироваться!")
            return
        await state.set_state(ChangeNameState.name)
        await call.message.answer("Введите новое имя", reply_markup=data_to_write)


@user_profile_router.message(ChangeNameState.name)
async def enter_new_name(message: Message, state: FSMContext) -> None:
    async with async_session_maker() as session:
        current_user_chat_id = message.chat.id
        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)

        player.name = message.text
        await state.clear()
        await session.commit()
        await message.answer("Успешно завершено!")


@user_profile_router.callback_query(ChangeLastNameCallBackData.filter(F.button_name == "change_last_name"))
async def change_last_name(call: CallbackQuery, callback_data: ChangeLastNameCallBackData, state: FSMContext):
    await state.clear()
    async with async_session_maker() as session:
        current_user_chat_id = call.message.chat.id
        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)
        if not player:
            await call.message.answer("У Вас не профиля, Вы должны зарегистрироваться!")
            return
        await state.set_state(ChangeLastNameState.last_name)
        await call.message.answer("Введите новую фамилию", reply_markup=data_to_write)


@user_profile_router.message(ChangeLastNameState.last_name)
async def enter_new_last_name(message: Message, state: FSMContext) -> None:
    async with async_session_maker() as session:
        current_user_chat_id = message.chat.id
        player_query = select(Player).filter_by(chat_id=current_user_chat_id)
        player = await get_obj(player_query, session)

        player.last_name = message.text
        await state.clear()
        await session.commit()
        await message.answer("Успешно завершено!")
