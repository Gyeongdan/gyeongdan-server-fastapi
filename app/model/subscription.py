from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String, event, Boolean, SmallInteger

from app.database.repository import Base

from enum import Enum


# class MailTypeCategory(Enum):



class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(CHAR(255), nullable=False)
    email_address = Column(String, nullable=False)
    category = Column(SmallInteger, index=True, nullable=False)
    status = Column(Boolean, index=True, nullable=False)  # true -> active , false -> unSubscribe
    created_at = Column(DateTime, default=datetime.now, nullable=False)

@event.listens_for(Subscription, "before_update", propagate=True)
def update_timestamp(mapper, connection, target):  # pylint: disable=unused-argument
    target.updated_at = datetime.now()
