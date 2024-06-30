from fastapi import APIRouter, Depends
from groq import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
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
    session: AsyncSession = Depends(get_db_session),
):
    article = await CrawlArticleService().crawl_article(
        news_type=articleCreateRequestDTO.publisher,
        url=articleCreateRequestDTO.url,
        session=session,
    )
    return GenericResponseDTO(
        data=article, message="Article extracted successfully", result=True
    )
