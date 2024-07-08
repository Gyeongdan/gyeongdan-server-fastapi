# newsletter_article.py

from datetime import datetime

from sqlalchemy import ARRAY, CHAR, BigInteger, Column, DateTime, String, Text

# Instead of "from sqlalchemy.ext.declarative import declarative_base"
from app.database.repository import Base


class NewsletterArticle(Base):
    __tablename__ = "newsletter_article"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 고유 식별자
    # 큰 크기가 필요하지 않아 SmallInteger를 사용
    category = Column(
        CHAR(255), nullable=False
    )  # 주제를 식별하는 인자 ex) 1: 경제, 2: 사회
    content = Column(Text, nullable=False)  # 쉽게 쓰여진 기사
    updated_at = Column(
        DateTime, default=datetime.now, nullable=False
    )  # 기사를 언제 받아왔는 지
    email_addresses = Column(ARRAY(String), nullable=True)
