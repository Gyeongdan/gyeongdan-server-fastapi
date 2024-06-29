# newsletter_article_service.py

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.newsletter_article import NewsletterArticle
from app.repository.newsletter_article_crud import NewsletterArticleRepository


class NewsletterService:
    async def create_article(
        self, category: int, content: str, session: AsyncSession
    ) -> NewsletterArticle:
        return await NewsletterArticleRepository().create(
            article_manager=NewsletterArticle(category=category, content=content),
            session=session,
        )

    async def get_content_by_id(
        self, id: int, session: AsyncSession
    ) -> NewsletterArticle:
        return await NewsletterArticleRepository().get_by_id(pk=id, session=session)

    async def get_all_contents(self, session: AsyncSession) -> List[NewsletterArticle]:
        return await NewsletterArticleRepository().get_all(session=session)

    async def get_content_by_category(
        self, category: int, session: AsyncSession
    ) -> List[NewsletterArticle]:
        return await NewsletterArticleRepository().get_by_category(
            category=category, session=session
        )

    async def update_content(
        self, id: int, category: int, content: str, session: AsyncSession
    ) -> NewsletterArticle:
        return await NewsletterArticleRepository().update_by_id(
            id=id, category=category, content=content, session=session
        )
