# send_email_manager.py

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, SmallInteger, BigInteger
# Instead of "from sqlalchemy.ext.declarative import declarative_base"
from app.database.repository import Base


class SendEmailManager(Base):
    __tablename__ = "send_email_manager"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 고유 식별자
    # 큰 크기가 필요하지 않아 SmallInteger를 사용
    category = Column(SmallInteger, nullable=False)  # 주제를 식별하는 인자 ex) 1: 경제, 2: 사회
    content = Column(Text, nullable=False)  # 쉽게 쓰여진 기사

#   나중에 다시 쓰자. 지금은 테스트
#    updated_at = Column(DateTime, default=datetime.now, nullable=False)  # 기사를 언제 받아왔는 지
