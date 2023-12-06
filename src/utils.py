from src.db.models import Player, Game
from src.db.db_connection import async_session_maker, Base

from sqlalchemy import select
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import InvalidRequestError

import logging

from src.exceptions import PlayerAlreadyAddedToGameException


async def register_player(chat_id: int, name: str, last_name: str):
    async with async_session_maker() as session:
        player = Player(chat_id=chat_id, name=name, last_name=last_name)
        session.add(player)
        await session.commit()


async def create_game(number_of_player: int, creator_chat_id: int, name: str) -> None:
    query = select(Player).filter_by(chat_id=creator_chat_id)
    creator = await get_obj(query)
    async with async_session_maker() as session:
        game = Game(name=name, number_of_player=number_of_player, creator_id=creator.id)
        session.add(game)
        await session.commit()


async def get_obj(query: Select) -> Base:
    async with async_session_maker() as session:
        result = await session.execute(query)
        return result.scalars().first()


async def add_player_to_game(player: Player, game: Game) -> None:

    # TODO Нужна проверка, что пользователь еще не состоит в игре
    async with async_session_maker() as session:
        game.players.append(player)
        session.add(game)
        await session.commit()
