from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.service.simple_article_service import generate_simple_article
from app.utils.generic_response import GenericResponseDTO
from app.model.simplified_article import SimplifiedArticle

simple_article_router = APIRouter()

class GenerateSimpleArticleRequestDTO(BaseModel):
    news_url: str
    news_publisher: str

@simple_article_router.post("/generate-simple-article", response_model=GenericResponseDTO[SimplifiedArticle])
async def generate_simple_article_(
    request: GenerateSimpleArticleRequestDTO,
    session: AsyncSession = Depends(get_db_session),
):
    simple_article = await generate_simple_article(
        publisher=request.news_publisher, url=request.news_url, session=session
    )

    return GenericResponseDTO(result=True, data=simple_article, message="Article generated successfully.")
