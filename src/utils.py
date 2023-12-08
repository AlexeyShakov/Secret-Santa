from copy import deepcopy
from typing import List, Optional

from aiogram import Bot

from src.db.models import Player, Game, GameResult
from src.db.db_connection import async_session_maker, Base

from sqlalchemy import select
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

import logging
import random

from src.exceptions import PlayerAlreadyAddedToGameException


async def register_player(chat_id: int, name: str, last_name: str):
    async with async_session_maker() as session:
        player = Player(chat_id=chat_id, name=name, last_name=last_name)
        session.add(player)
        await session.commit()


async def create_game(number_of_player: int, creator_chat_id: int, name: str) -> None:
    async with async_session_maker() as session:
        query = select(Player).filter_by(chat_id=creator_chat_id)
        creator = await get_obj(query, session)
        game = Game(name=name, number_of_player=number_of_player, creator_id=creator.id)
        session.add(game)
        await session.commit()


async def get_obj(query: Select, session) -> Optional[Base]:
    result = await session.execute(query)
    return result.scalars().first()


async def add_player_to_game(player: Player, game: Game, session: AsyncSession, bot: Bot) -> None:
    game.players.append(player)
    session.add(game)
    await session.commit()
    if len(game.players) == game.number_of_player - 1:
        await bot.send_message(chat_id=game.creator.chat_id, text=f"Все игроки присоединились к игре {game.name}")


async def find_matches(game: Game, session: AsyncSession) -> dict[Player, Player]:
    matches = dict()
    players: List[Player] = game.players
    players.append(game.creator)

    candidates: List[Player] = deepcopy(players)

    for player in players:
        while True:
            print("Я в бесконечно цикле")
            gift_getter: Player = random.choice(candidates)
            if gift_getter.chat_id == player.chat_id:
                print("CONT")
                continue
            matches[player] = gift_getter
            candidates.remove(gift_getter)
            break
    print("Вышел")
    # formatted_matches = {f"{player.name} {player.last_name}": f"{gift_getter.name} {gift_getter.last_name}" for player, gift_getter in matches.items()}
    game_result = GameResult(matches=matches, game=game)
    session.add(game_result)
    return matches
