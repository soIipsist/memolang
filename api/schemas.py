from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Optional, List
from enums import GameType


class RoleCreate(BaseModel):
    name: str = None


class RoleOut(BaseModel):
    id: Optional[int] = None
    name: str = None


class UserBase(BaseModel):
    id: int
    username: Optional[str] = None
    password: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str

    created_at: Optional[datetime] = None
    default_proxy: Optional[str] = None
    default_user_agent: Optional[str] = None


class UserOut(BaseModel):
    id: Optional[int] = None
    username: str

    default_proxy: Optional[str] = None
    default_user_agent: Optional[str] = None


class TokenCreate(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class GameCreate(BaseModel):
    id: Optional[int] = None
    game_type = GameType.WORDS
    users: List[UserBase]
    frequency: int = 100


class GameOut(BaseModel):
    id: Optional[int] = None
    game_type: GameType
    users: List[UserBase]
    frequency: int
    score: int
