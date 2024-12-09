from fastapi import Depends, FastAPI, HTTPException, Header, Request, status, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uvicorn

from utils.hash_utils import verify_password
from utils.model_utils import (
    upsert_model_to_db,
    insert_model_to_db,
    convert_model_to_schema,
    convert_schema_to_model,
)

from constants import *

from api.database import (
    SessionLocal,
    engine,
    get_db,
    Base,
)

from utils.oauth2 import (
    create_access_token,
    extract_token_from_request,
    invalidate_access_token,
    get_current_user,
    verify_access_token,
)

from models.user import User, Role
from api.schemas import TokenCreate, UserCreate, UserOut
from api.routers.user import router as user_router

app = FastAPI()


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    detail = {"detail": "Database error: Unique constraint violation"}
    return JSONResponse(status_code=422, content=detail)


Base.metadata.create_all(engine)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)


@app.get("/", tags=["Main"])
def main():
    return RedirectResponse(url="http://127.0.0.1:8000/docs")


@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    user_model = convert_schema_to_model(user, User)
    user_model = create_role(db, "user", user_model)

    user_model = insert_model_to_db(db, user_model, User)
    return user_model


@app.post("/login", tags=["Main"], response_model=TokenCreate)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(
            User.username == user_credentials.username,
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials"
        )

    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials"
        )

    # create a token
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/logout", tags=["Main"])
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Invalidate the token
    token = extract_token_from_request(request)

    if token:
        invalidate_access_token(token)
        response.delete_cookie("access_token")

    return {"message": "Successfully logged out"}


if __name__ == "__main__":
    uvicorn.run("api.main:app", reload=True, log_level="debug")
