from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.repository import Base

class ArticleRelatedDocument(Base):
    __tablename__ = 'article_related_documents'
    __table_args__ = {'schema': 'gyeongdan'}
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('gyeongdan.articles.id', ondelete='CASCADE'))
    title = Column(String(255), nullable=False)
    link = Column(String(255), default='URL 없음')
    snippet = Column(Text)

    article = relationship("Articles", back_populates="related_documents")
