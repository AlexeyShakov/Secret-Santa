from src.db.models import Player, Game
from src.db.db_connection import async_session_maker

from sqlalchemy import select

async def register_player(chat_id: int, name: str, last_name: str):
    async with async_session_maker() as session:
        player = Player(chat_id=chat_id, name=name, last_name=last_name)
        session.add(player)
        await session.commit()


async def create_game(number_of_player: int, creator_chat_id: int, name: str) -> None:
    creator = await _get_creator(creator_chat_id=creator_chat_id)
    async with async_session_maker() as session:
        game = Game(name=name, number_of_player=number_of_player, creator_id=creator.id)
        session.add(game)
        await session.commit()

async def _get_creator(creator_chat_id: int) -> Player:
    query = select(Player).filter_by(chat_id=creator_chat_id)
    async with async_session_maker() as session:
        result = await session.execute(query)
        return result.scalars().first()
