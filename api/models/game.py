from sqlalchemy import Column, String, Integer
from api.database import Base

from enums import GameType


class Game(Base):
    __tablename__ = "games"
    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    game_type = Column(GameType, nullable=False, default=GameType.WORDS)
    score = Column(Integer, nullable=True)
