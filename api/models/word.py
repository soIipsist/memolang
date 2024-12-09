from unittest.mock import Base
from fastapi import requests
from sqlalchemy import Integer, Table, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from constants import *


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, autoincrement=True, primary_key=True)
    word = Column(String, nullable=False)
    language_id = Column(String)
