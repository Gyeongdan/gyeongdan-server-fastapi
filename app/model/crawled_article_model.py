from sqlalchemy import Column, Integer, String, Text, Enum as SQLAlchemyEnum, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class NewspaperEnum(enum.Enum):
    mk = "매일경제"
    hankyung = "한국경제"
    sedaily = "서울경제"

class CrawledArticle(Base):
    __tablename__ = 'crawled_articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    newspaper = Column(SQLAlchemyEnum(NewspaperEnum), nullable=False)
    regenerated_content = Column(Text, nullable=True)
