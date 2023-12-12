from typing import List

from sqlalchemy.orm import relationship
from sqlalchemy import Integer, Column, String, SmallInteger, CheckConstraint, Table, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

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
    number_of_player: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    creator_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    creator: Mapped["Player"] = relationship(back_populates="creator_games", lazy="subquery")

    players: Mapped[List["Player"]] = relationship(secondary=association_table, back_populates="games", lazy="subquery")
    game_results: Mapped[List["GameResult"]] = relationship(back_populates="game")

    __table_args__ = (
        CheckConstraint(number_of_player > 0, name="check_bar_positive"),
        {},
    )


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(length=25), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=25), nullable=False)

    creator_games: Mapped[List[Game]] = relationship(back_populates="creator", cascade="all, delete")
    creator_reviews: Mapped[List[Game]] = relationship(back_populates="review_creator", cascade="all, delete")

    games: Mapped[List[Game]] = relationship(secondary=association_table, back_populates="players")


class GameResult(Base):
    __tablename__ = "game_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    matches: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB))

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    game: Mapped[Game] = relationship(back_populates="game_results", lazy="subquery")


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    creator_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=True)
    review_creator: Mapped["Player"] = relationship(back_populates="creator_reviews", lazy="subquery")
