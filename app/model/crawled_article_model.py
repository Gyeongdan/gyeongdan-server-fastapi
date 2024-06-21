from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAEnum, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional
from datetime import datetime

Base = declarative_base()

class NewspaperEnum(Enum):
    MK = "MK"  # 매일경제
    HK = "HK"  # 한국경제
    SK = "SK"  # 서울경제

class RegenerationModelEnum(Enum):
    LLAMA3 = 'LLAMA3'
    GPT4 = 'GPT4'

class CrawledArticle(Base):
    __tablename__ = "crawled_articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    newspaper = Column(SQLAEnum(NewspaperEnum), nullable=False)
    url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_regenerated = Column(Boolean, default=False, nullable=False)
    regeneration_model = Column(SQLAEnum(RegenerationModelEnum), nullable=False)
    regenerated_content = Column(Text, nullable=True)

class CrawledArticleBase(BaseModel):
    url: str
    title: str
    content: str
    newspaper: NewspaperEnum
    regenerated_content: Optional[str] = None
    is_regenerated: bool = False
    regeneration_model : RegenerationModelEnum

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