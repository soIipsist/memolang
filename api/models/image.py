from sqlalchemy import Column, String
from api.database import Base


class Image(Base):
    __tablename__ = "images"
    id = Column(String, primary_key=True, nullable=False)
    link = Column(String, nullable=False)
