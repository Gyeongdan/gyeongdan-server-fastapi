from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String, event, Boolean, SmallInteger

from app.database.repository import Base


class EmailAddress(Base):
    __tablename__ = "email_addresses"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    emailAddress = Column(String, nullable=False)
    name = Column(CHAR(255), nullable=False)
    category = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    valid = Column(Boolean, nullable=False)



@event.listens_for(EmailAddress, "before_update", propagate=True)
def update_timestamp(mapper, connection, target):  # pylint: disable=unused-argument
    target.updated_at = datetime.now()
