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
    # Нужен для дополнительной проверки.Допустим играет 3 человека юзер1, юзер2 и юзер3(создатель). Если юзер1
    # будет сантой для юзер 2, а юзер 2 будет сантой для юзер 1, То получится так, что останется один юзер3. И я окажусь
    # в бесконечном цикле. Поэтому я завожу словарь, где ключом будет игрок, кто получает подарок, а значением тайный санта
    getter_santa_mapping = dict()

    players: List[Player] = deepcopy(game.players)
    players.append(game.creator)

    candidates: List[Player] = deepcopy(players)

    for player in players:
        while True:
            gift_getter: Player = random.choice(candidates)
            if gift_getter.chat_id == player.chat_id:
                continue
            if player.chat_id in getter_santa_mapping and getter_santa_mapping[player.chat_id] == gift_getter.chat_id:
                continue
            matches[player] = gift_getter
            getter_santa_mapping[gift_getter.chat_id] = player.chat_id
            candidates.remove(gift_getter)
            break

    formatted_matches = {f"{player.name} {player.last_name}": f"{gift_getter.name} {gift_getter.last_name}" for player, gift_getter in matches.items()}
    game_result = GameResult(matches=formatted_matches, game=game)
    game.is_active = False

    session.add_all([game_result, game])
    return matches
