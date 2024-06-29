# newsletter_article_crud.py


import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import get_repository, model_to_dict
from app.model.newsletter_article import NewsletterArticle


class NewsletterArticleRepository:
    async def create(self, article_manager: NewsletterArticle, session: AsyncSession):
        repository = get_repository(NewsletterArticle)(session)
        return await repository.create(model_to_dict(article_manager))

    async def get_by_id(self, pk: int, session: AsyncSession):
        repository = get_repository(NewsletterArticle)(session)
        content = await repository.get(pk)
        if content is None:
            raise HTTPException(
                status_code=404, detail="해당 순번이 존재하지 않습니다."
            )
        return content

    async def get_all(self, session: AsyncSession):
        repository = get_repository(NewsletterArticle)(session)
        return await repository.filter()

    async def get_by_category(self, category: int, session: AsyncSession):
        result = await session.execute(
            select(NewsletterArticle).where(NewsletterArticle.category == category)
        )
        return result.scalars().all()

    async def update_by_id(
        self, id: int, category: int, content: str, session: AsyncSession
    ):
        repository = get_repository(NewsletterArticle)(session)
        now_time = datetime.datetime.now()
        return await repository.update_by_pk(
            pk=id,
            data={"category": category, "content": content, "updated_at": now_time},
        )
