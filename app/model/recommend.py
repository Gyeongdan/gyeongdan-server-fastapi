from sqlalchemy import BigInteger, Column, ARRAY, Integer

from app.database.repository import Base


class Recommend(Base):
    __tablename__ = "recommends"
    __table_args__ = {"schema": "gyeongdan"}

    classification_id = Column(BigInteger, primary_key=True, index=True)
    recommend_article_ids = Column(ARRAY(Integer), nullable=True)
