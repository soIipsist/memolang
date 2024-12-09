from sqlalchemy import Column, String
from api.database import Base


class Language(Base):
    __tablename__ = "languages"
    id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
