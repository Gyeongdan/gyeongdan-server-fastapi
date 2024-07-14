from enum import Enum

from sqlalchemy import BigInteger, Column, Integer

from app.database.repository import Base


class UserType(Base):
    __tablename__ = "user_type"

    user_id = Column(BigInteger, primary_key=True, index=True)
    user_type_issue_finder = Column(Integer, nullable=True)
    user_type_lifestyle_consumer = Column(Integer, nullable=True)
    user_type_entertainer = Column(Integer, nullable=True)
    user_type_tech_specialist = Column(Integer, nullable=True)
    user_type_professionals = Column(Integer, nullable=True)


class UserTypes(Enum):
    NONE: -1
    ISSUE_FINDER: 0
    LIFESTYLE_CONSUMER: 1
    ENTERTAINER: 2
    TECH_SEPCIALIST: 3
    PROFESSIONALS: 4
