from fastapi import APIRouter
from api.database import get_db
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import any_
from api.schemas import RoleOut, UserCreate, UserOut, RoleCreate
from utils.oauth2 import get_current_user_with_roles, get_current_user
from utils.model_utils import insert_model_to_db, upsert_model_to_db
from models.user import User, Role
from models.game import Game
from schemas import Game

router = APIRouter(prefix="/games", tags=["Games"])


@router.get("/{game_id}")
def get_game(db: Session = Depends(get_db)):
    return


@router.post("/")
def create_game(game: Game, db: Session = Depends(get_db)):
    return
