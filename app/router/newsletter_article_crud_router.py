# newsletter_article_crud_router.py

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.model.newsletter_article import NewsletterArticle
from app.model.subscription import MailTypeCategory
from app.service.newsletter_article_service import NewsletterService
from app.utils.generic_response import GenericResponseDTO

newsletter_article_router = APIRouter()


class NewsletterArticleResponseDTO(BaseModel):
    category: str
    content: str
    updated_at: datetime


async def newsletter_to_dto(newsletter_article: NewsletterArticle):
    return NewsletterArticleResponseDTO(
        category=newsletter_article.category,
        content=newsletter_article.content,
        updated_at=newsletter_article.updated_at,
    )


async def list_to_dto_list(newsletter_article: List[NewsletterArticle]):
    return [await newsletter_to_dto(article) for article in newsletter_article]


@newsletter_article_router.post(
    "/newsletter_article/save", response_model=GenericResponseDTO[int]
)
async def create_manager(
    category: MailTypeCategory,
    content: str,
    session: AsyncSession = Depends(get_db_session),
):
    newsletter_article = await NewsletterService().create_article(
        category, content, session
    )
    return GenericResponseDTO[int](
        data=newsletter_article.id, message="Successfully Done", result=True
    )


@newsletter_article_router.get(
    "/newsletter_article/{id}",
    response_model=GenericResponseDTO[NewsletterArticleResponseDTO],
)
async def get_content_by_id(id: int, session: AsyncSession = Depends(get_db_session)):
    newsletter_article = await NewsletterService().get_content_by_id(id, session)
    return GenericResponseDTO[NewsletterArticleResponseDTO](
        data=await newsletter_to_dto(newsletter_article),
        message="Successfully Done",
        result=True,
    )


@newsletter_article_router.get(
    "/newsletter_article",
    response_model=GenericResponseDTO[List[NewsletterArticleResponseDTO]],
)
async def get_all(session: AsyncSession = Depends(get_db_session)):
    newsletter_article = await NewsletterService().get_all_contents(session)
    dummy = await list_to_dto_list(newsletter_article)
    return GenericResponseDTO[List[NewsletterArticleResponseDTO]](
        data=dummy, message="Successfully Done", result=True
    )


@newsletter_article_router.get(
    "/newsletter_article/search/{category}",
    response_model=GenericResponseDTO[List[NewsletterArticleResponseDTO]],
)
async def get_content_by_category(
    category: MailTypeCategory, session: AsyncSession = Depends(get_db_session)
):
    newsletter_article = await NewsletterService().get_content_by_category(
        category, session
    )
    newsletter_article_dto = await list_to_dto_list(newsletter_article)
    return GenericResponseDTO[List[NewsletterArticleResponseDTO]](
        data=newsletter_article_dto, message="Successfully Done", result=True
    )


@newsletter_article_router.put(
    "/newsletter_article/update", response_model=GenericResponseDTO[int]
)
async def update_content_by_id(
    id: int,
    category: MailTypeCategory,
    content: str,
    session: AsyncSession = Depends(get_db_session),
):
    newsletter_article = await NewsletterService().update_content(
        id, category, content, session
    )
    return GenericResponseDTO[int](
        data=newsletter_article.id, message="Successfully Done", result=True
    )
