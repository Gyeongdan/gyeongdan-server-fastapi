from datetime import datetime
from enum import Enum

from sqlalchemy import CHAR, BigInteger, Boolean, Column, DateTime, String, event

from app.database.repository import Base


class MailTypeCategory(Enum):
    ECONOMY_AND_BUSINESS = "Economy and Business"
    POLITICS_AND_SOCIETY = "Politics and Society"
    TECHNOLOGY_AND_CULTURE = "Technology and Culture"
    SPORTS_AND_LEISURE = "Sports and Leisure"
    OPINION_AND_ANALYSIS = "Opinion and Analysis"


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
