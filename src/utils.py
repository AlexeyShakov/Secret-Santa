from src.db.models import Player
from src.db.db_connection import async_session_maker



async def register_player(chat_id: int, name: str, last_name: str):
    async with async_session_maker() as session:
        player = Player(chat_id=chat_id, name=name, last_name=last_name)
        session.add(player)
        await session.commit()
