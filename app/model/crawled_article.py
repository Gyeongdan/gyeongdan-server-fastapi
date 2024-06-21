from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String, Text, event

from app.database.repository import Base


class CrawledArticle(Base):
    __tablename__ = "crawled_articles"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    url = Column(String, nullable=False)
    publisher = Column(CHAR(255), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, nullable=False)


@event.listens_for(CrawledArticle, "before_update", propagate=True)
def update_timestamp(mapper, connection, target):  # pylint: disable=unused-argument
    target.updated_at = datetime.now()
