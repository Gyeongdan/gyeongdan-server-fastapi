from fastapi import APIRouter
from app.model.article_model import ArticleResponse
from app.service.crawl_article_service import extract_article
from app.service.crawl_mk import extract_article_mk
from app.service.crawl_hk import extract_article_hk
from app.service.crawl_sedaily import extract_article_sedaily

news_scrap_rotuer = APIRouter()

@news_scrap_rotuer.get("/extract-article/{news_type}", response_model=ArticleResponse)
async def extract_article_api(news_type: str, url: str):
    return await extract_article(news_type, url)

@news_scrap_rotuer.get("/mk_news", response_model=ArticleResponse)
async def extract_article_api_mk(url: str):
    return await extract_article_mk(url)

@news_scrap_rotuer.get("/hk_news", response_model=ArticleResponse)
async def extract_article_api_hk(url: str):
    return await extract_article_hk(url)

@news_scrap_rotuer.get("/sedaily_news", response_model=ArticleResponse)
async def extract_article_api_sedaily(url: str):
    return await extract_article_sedaily(url)