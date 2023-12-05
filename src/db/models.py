from sqlalchemy.orm import relationship
from sqlalchemy import Integer, Column, String, SmallInteger, CheckConstraint

from .db_connection import Base


# TODO сделать связь многие ко многим!!!!!

class Game(Base):
    """
    1. Уникальный хэш
    2. Количество участников

    """
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    number_of_player = Column(SmallInteger, nullable=False)

    __table_args__ = (
        CheckConstraint(number_of_player > 0, name="check_bar_positive"),
        {},
    )


class Player(Base):
    """
    1 Чайт айди
    2. Имя пользователя
    Нужно регистрировать пользователя перед тем, как он будет присоединятся к игре или создавать игру
    """
    ____tablename__ = "players"

    id = Column(Integer, primary_key=True)
    chat_id = Column(String(length=40), nullable=False, unique=True)
    name = Column(String(length=25), nullable=False)
    last_name = Column(String(length=25), nullable=False)
