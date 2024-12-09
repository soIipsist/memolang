import random
import string
from typing import Optional
from jose import JWTError, jwt
import datetime
import os

from models.user import User
from fastapi import Depends, Request, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from api.database import get_db
from api.config import Settings

from api.schemas import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

settings = Settings()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def invalidate_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as e:
        print("EXCEPTION:", e)
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_access_token(token: str, raise_exception: bool = True):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            if raise_exception:
                raise credentials_exception
            else:
                return None

        if isinstance(id, int):
            id = str(id)
        token_data = TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):

    token = verify_access_token(token, True)
    user = db.query(User).filter(User.id == token.id).first()

    return user


def extract_token_from_request(request: Request):
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        return token.split(" ")[1]
    return None


def get_token_optional(request: Request) -> Optional[str]:
    authorization: str = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization[len("Bearer ") :]
    return None


def get_optional_user(
    token: Optional[str] = Depends(get_token_optional), db: Session = Depends(get_db)
) -> Optional[User]:
    if token is None:
        return None

    try:
        return get_current_user(token, db)
    except HTTPException:
        return None


def get_current_user_with_roles(required_roles: list[str] = ["admin"]):
    def role_checker(current_user: User = Depends(get_current_user)):
        user_roles = [role.name for role in current_user.roles]
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user

    return role_checker
