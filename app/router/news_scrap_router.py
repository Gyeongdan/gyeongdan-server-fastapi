from fastapi import APIRouter

from app.model.article_model import ArticleResponse
from app.service.crawl_article_service import extract_article

news_scrap_rotuer = APIRouter()


@news_scrap_rotuer.get("/extract-article/{news_type}", response_model=ArticleResponse)
async def extract_article_api(news_type: str, url: str):
    return await extract_article(news_type, url)
