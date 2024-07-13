from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String, Text, JSON, Enum, event, Integer
from sqlalchemy.dialects.postgresql import JSONB

from app.database.repository import Base

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
    phrase = Column(JSONB, nullable=True)
    comment = Column(Text, nullable=True)
    category = Column(CHAR(255), nullable=True)
    probability_issue_finder = Column(Integer, nullable=True)
    probability_lifestyle_consumer = Column(Integer, nullable=True)
    probability_entertainer = Column(Integer, nullable=True)
    probability_tech_specialist = Column(Integer, nullable=True)
    probability_professionals = Column(Integer, nullable=True)

@event.listens_for(Articles, "before_update", propagate=True)
def update_timestamp(mapper, connection, target):  # pylint: disable=unused-argument
    target.updated_at = datetime.now()
