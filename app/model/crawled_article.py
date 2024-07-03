from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String, Text, JSON, Enum, event

from app.database.repository import Base

import enum

class CategoryEnum(enum.Enum):
    ECONOMY_AND_BUSINESS = "경제 및 기업"
    POLITICS_AND_SOCIETY = "정치 및 사회"
    TECHNOLOGY_AND_CULTURE = "기술 및 문화"
    SPORTS_AND_LEISURE = "스포츠 및 여가"
    OPINION_AND_ANALYSIS = "오피니언 및 분석"

class Articles(Base):
    __tablename__ = "articles"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    url = Column(String, nullable=False)
    publisher = Column(CHAR(255), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    simple_title = Column(Text, nullable=True)
    simple_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, nullable=False)
    phrase = Column(JSON, nullable=True)
    comment = Column(Text, nullable=True)
    category = Column(Enum(CategoryEnum), nullable=True)

@event.listens_for(Articles, "before_update", propagate=True)
def update_timestamp(mapper, connection, target):  # pylint: disable=unused-argument
    target.updated_at = datetime.now()
