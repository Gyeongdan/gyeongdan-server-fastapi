from fastapi import APIRouter
from app.model.article_model import ArticleResponse
from app.service.news_scrap_service import extract_article

news_scrapping_router = APIRouter()

@news_scrapping_router.get("/extract-article", response_model=ArticleResponse)
async def extract_article_api(url: str):
    return await extract_article(url)
