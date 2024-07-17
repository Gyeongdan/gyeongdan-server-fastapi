from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.repository import Base

class ArticleRelatedDocument(Base):
    __tablename__ = 'article_related_documents'

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'))
    title = Column(String, index=True)
    link = Column(String)
    snippet = Column(Text)

    article = relationship("Article", back_populates="related_documents")
