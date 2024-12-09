import datetime
from fastapi import requests
from sqlalchemy import Integer, Table, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from constants import *
from constants import BASE_URL
import requests
from api.database import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role(name={self.name}, id={self.id})>"

    def __str__(self) -> str:
        return f"<Role(name={self.name}, id={self.id})>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    token = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    def __str__(self) -> str:
        return (
            f"<User(username={self.username}, roles={self.roles}, token={self.token})>"
        )

    def __repr__(self):
        return (
            f"<User(username={self.username}, roles={self.roles}, token={self.token})>"
        )

    def login(self):
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": self.username, "password": self.password},
        ).json()

        response: dict
        self.token = response.get("access_token")

        return self.token

    def logout(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{BASE_URL}/logout", headers=headers)
        self.token = None
        print(response.text)
