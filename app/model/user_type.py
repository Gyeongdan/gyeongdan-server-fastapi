from enum import Enum

from pydantic import BaseModel
from sqlalchemy import CHAR, BigInteger, Column, Integer

from app.database.repository import Base


class UserType(Base):
    __tablename__ = "user_type"
    __table_args__ = {"schema": "gyeongdan"}

    user_id = Column(BigInteger, primary_key=True, index=True)
    user_type_issue_finder = Column(Integer, nullable=True)
    user_type_lifestyle_consumer = Column(Integer, nullable=True)
    user_type_entertainer = Column(Integer, nullable=True)
    user_type_tech_specialist = Column(Integer, nullable=True)
    user_type_professionals = Column(Integer, nullable=True)
    user_type = Column(CHAR(255), nullable=True)


class UserTypes(Enum):
    NONE = {"id": -1, "name": "NONE"}
    ISSUE_FINDER = {"id": 0, "name": "ISSUE_FINDER"}
    LIFESTYLE_CONSUMER = {"id": 1, "name": "LIFESTYLE_CONSUMER"}
    ENTERTAINER = {"id": 2, "name": "ENTERTAINER"}
    TECH_SPECIALIST = {"id": 3, "name": "TECH_SPECIALIST"}
    PROFESSIONALS = {"id": 4, "name": "PROFESSIONALS"}

    @classmethod
    def get_by_name(cls, name: str):
        for user_type in cls:
            if user_type.name.lower() == name.lower():
                return user_type
        return cls.NONE


class UserTypePercent(BaseModel):
    issueFinder: int
    lifestyleConsumer: int
    entertainer: int
    techSpecialist: int
    professionals: int

    def get_dominant_type(self) -> str:
        type_percentages = self.dict()
        max_value = 0
        dominant_type = UserTypes.LIFESTYLE_CONSUMER

        for key, value in type_percentages.items():
            if value > max_value:
                max_value = value
                user_type = UserTypes.get_by_name(key)
                if user_type:
                    dominant_type = user_type
        if dominant_type == UserTypes.NONE:
            return UserTypes.LIFESTYLE_CONSUMER.name
        return dominant_type.name
