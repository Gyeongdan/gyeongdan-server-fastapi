from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.article_publisher import Publisher
from app.model.crawled_article import CrawledArticle
from app.repository.crawled_article_crud import CrawledArticleRepository


class ArticleManageService:
    async def create_article(
        self,
        url: str,
        publisher: Publisher,
        title: str,
        content: str,
        session: AsyncSession,
    ) -> CrawledArticle:
        return await CrawledArticleRepository().create(
            article=CrawledArticle(
                url=url,
                title=title,
                content=content,
                publisher=publisher.name,
            ),
            session=session,
        )

    async def update_simplified_article(
        self, id: int, simplified_content: str, session: AsyncSession
    ) -> CrawledArticle:
        return await CrawledArticleRepository().update_simplified_content(
            id=id, simplified_content=simplified_content, session=session
        )

    async def get_article_by_id(
        self, article_id: int, session: AsyncSession
    ) -> CrawledArticle:
        return await CrawledArticleRepository().get(pk=article_id, session=session)

    async def get_all_articles(self, session: AsyncSession) -> List[CrawledArticle]:
        return await CrawledArticleRepository().get_all(session=session)
