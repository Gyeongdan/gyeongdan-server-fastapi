# api_visualization.py

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String, Text

from app.database.repository import Base


class ApiVisualization(Base):
    __tablename__ = "api_visualization"
    __table_args__ = {"schema": "gyeongdan"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 고유 식별자
    title = Column(String, nullable=False)  # 제목
    content = Column(Text, nullable=False)  # 본문
    graph_html = Column(Text, nullable=False)  # html 데이터
    create_at = Column(DateTime, default=datetime.now, nullable=False)
