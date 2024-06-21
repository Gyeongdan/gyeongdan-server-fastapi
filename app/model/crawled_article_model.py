from sqlalchemy import Column, Integer, String, func, DateTime, Enum as SQLAEnum, Text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional
from datetime import datetime

Base = declarative_base()

class NewspaperEnum(Enum):
    매일경제 = '매일경제'
    한국경제 = '한국경제'
    서울경제 = '서울경제'

class CrawledArticle(Base):
    __tablename__ = "crawled_articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    newspaper = Column(SQLAEnum(NewspaperEnum), nullable=False)
    regenerated_content = Column(Text, nullable=True)

class CrawledArticleBase(BaseModel):
    url: str
    title: str
    content: str
    newspaper: NewspaperEnum
    regenerated_content: Optional[str] = None

    @validator('newspaper', pre=True)
    def validate_newspaper(cls, value):
        if value not in NewspaperEnum._value2member_map_:
            raise ValueError(f"Newspaper must be one of {[e.value for e in NewspaperEnum]}")
        return value

class CrawledArticleCreate(CrawledArticleBase):
    pass

class CrawledArticleUpdate(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    newspaper: Optional[NewspaperEnum] = None
    regenerated_content: Optional[str] = None

    @validator('newspaper', pre=True, always=True)
    def validate_newspaper(cls, value):
        if value is not None and value not in NewspaperEnum._value2member_map_:
            raise ValueError(f"Newspaper must be one of {[e.value for e in NewspaperEnum]}")
        return value

class CrawledArticleSchema(CrawledArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic V2 설정
