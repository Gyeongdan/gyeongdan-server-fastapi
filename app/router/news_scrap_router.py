from fastapi import APIRouter
from groq import BaseModel

from app.model.article_model import ArticleResponse
from app.service.crawl_article_service import CrawlArticleService
from app.utils.generic_response import GenericResponseDTO

news_scrap_rotuer = APIRouter()


class ArticleCreateRequestDTO(BaseModel):
    url: str
    publisher: str


@news_scrap_rotuer.post(
    "/extract-article", response_model=GenericResponseDTO[ArticleResponse]
)
async def extract_article_api(
    articleCreateRequestDTO: ArticleCreateRequestDTO,
):
    article = await CrawlArticleService().crawl_article(
        news_type=articleCreateRequestDTO.publisher,
        url=articleCreateRequestDTO.url,
    )
    return GenericResponseDTO(
        data=article, message="Article extracted successfully", result=True
    )
