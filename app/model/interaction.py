from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, Column, Integer

from app.database.repository import Base


class Interaction(Base):
    __tablename__ = "interactions"

    classification_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    article_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    duration_time = Column(Integer)

