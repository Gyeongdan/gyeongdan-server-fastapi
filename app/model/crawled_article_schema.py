from pydantic import BaseModel
from typing import Optional
from enum import Enum

class NewspaperEnum(str, Enum):
    mk = "매일경제"
    hankyung = "한국경제"
    sedaily = "서울경제"

class CrawledArticleBase(BaseModel):
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    newspaper: NewspaperEnum
    regenerated_content: Optional[str] = None

class CrawledArticleCreate(CrawledArticleBase):
    pass

class CrawledArticleUpdate(CrawledArticleBase):
    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    newspaper: Optional[NewspaperEnum] = None
    regenerated_content: Optional[str] = None

class CrawledArticle(CrawledArticleBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True
