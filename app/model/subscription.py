from datetime import datetime
from enum import Enum

from sqlalchemy import CHAR, BigInteger, Boolean, Column, DateTime, String, event

from app.database.repository import Base


class MailTypeCategory(Enum):
    ECONOMY_AND_BUSINESS = "ECONOMY_AND_BUSINESS"  # 경제와 비즈니스
    POLITICS_AND_SOCIETY = "POLITICS_AND_SOCIETY"  # 정치와 사회
    TECHNOLOGY_AND_CULTURE = "TECHNOLOGY_AND_CULTURE"  # 기술과 문화
    SPORTS_AND_LEISURE = "SPORTS_AND_LEISURE"  # 스포츠와 여가
    OPINION_AND_ANALYSIS = "OPINION_AND_ANALYSIS"  # 의견과 분석


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(CHAR(255), nullable=False)
    email_address = Column(String, nullable=False)
    category = Column(CHAR(255), nullable=False)
    status = Column(Boolean, nullable=False)  # true -> active , false -> unSubscribe
    created_at = Column(DateTime, default=datetime.now, nullable=False)


@event.listens_for(Subscription, "before_update", propagate=True)
def update_timestamp(mapper, connection, target):  # pylint: disable=unused-argument
    target.updated_at = datetime.now()
