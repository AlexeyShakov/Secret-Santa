from typing import List

from sqlalchemy.orm import relationship
from sqlalchemy import Integer, Column, String, SmallInteger, CheckConstraint, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .db_connection import Base


association_table = Table(
    "association_table",
    Base.metadata,
    Column("game_id", ForeignKey("games.id"), primary_key=True),
    Column("player_id", ForeignKey("players.id"), primary_key=True),
)

class Game(Base):

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(length=10), unique=True)
    number_of_player: Mapped[int] = Column(SmallInteger, nullable=False)
    creator: Mapped["Player"] = relationship()

    players: Mapped[List["Player"]] = relationship(secondary=association_table, back_populates="games")

    __table_args__ = (
        CheckConstraint(number_of_player > 0, name="check_bar_positive"),
        {},
    )


class Player(Base):
    ____tablename__ = "players"

    id = Column(Integer, primary_key=True)
    chat_id = Column(String(length=40), nullable=False, unique=True)
    name = Column(String(length=25), nullable=False)
    last_name = Column(String(length=25), nullable=False)

    games: Mapped[List[Game]] = relationship(secondary=association_table, back_populates="players")
