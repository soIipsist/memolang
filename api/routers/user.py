from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import any_
from api.schemas import RoleOut, UserCreate, UserOut, RoleCreate
from utils.oauth2 import get_current_user_with_roles, get_current_user
from utils.model_utils import insert_model_to_db, upsert_model_to_db
from models.user import User, Role
from api.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


def create_role(db: Session, role_name: str, user_model: User):
    role = db.query(Role).filter(Role.name == role_name).first()

    if role:
        user_model.roles.append(role)
    else:
        # create the role if it doesn't exist
        new_role = Role(name=role_name)

        db.add(new_role)
        db.commit()
        user_model.roles.append(new_role)

    return user_model


@router.get("/", response_model=List[UserOut])
async def get_users(
    user_id: Optional[str] = Query(None),
    role_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_with_roles()),
):
    query = db.query(User)

    if user_id:
        query = query.filter(User.id == user_id)

    if role_name:
        query = query.filter(role_name == any_(User.roles))

    return query.all()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    print(user.roles)
    if user.id == user_id or user.roles == ["admin"]:
        pass

    user = db.query(User).filter(User.id == user_id).first()

    if user:
        user.delete(synchronize_session=False)
        db.commit()
        return user_id

    raise HTTPException(status_code=404)


@router.get(
    "/{user_id}/roles",
    response_model=List[RoleOut],
)
def get_user_roles(
    user_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found.",
        )

    return user.roles


@router.post(
    "/{user_id}/roles",
    status_code=status.HTTP_201_CREATED,
    response_model=List[RoleOut],
)
def create_user_role(
    user_id: int,
    role: RoleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_with_roles()),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found.",
        )

    user = create_role(db, role.name, user)
    user = upsert_model_to_db(db, user, User, (User.id == user.id))
    return user.roles
