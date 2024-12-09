from sqlalchemy import Column, Enum, ForeignKey, String, Integer, Table
from sqlalchemy.orm import relationship
from api.database import Base
from enums import GameType

# Association table for the many-to-many relationship
game_user_association = Table(
    "game_user_association",
    Base.metadata,
    Column("game_id", String, ForeignKey("games.id"), primary_key=True),
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
)


class GameScore(Base):
    __tablename__ = "game_scores"
    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    score = Column(Integer, nullable=False)
    user = relationship("User", back_populates="scores")
    game = relationship("Game", back_populates="scores")


class Game(Base):
    __tablename__ = "games"
    id = Column(String, primary_key=True, nullable=False)
    game_type = Column(Enum(GameType), nullable=False, default=GameType.WORDS)
    frequency = Column(Integer, nullable=True, default=100)

    users = relationship(
        "User", secondary=game_user_association, back_populates="games"
    )
    scores = relationship("GameScore", back_populates="game")
