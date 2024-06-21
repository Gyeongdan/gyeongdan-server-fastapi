from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.article_publisher import find_publisher
from app.model.crawled_article import CrawledArticle
from app.repository.crawled_article_crud import CrawledArticleRepository


class ArticleService:
    async def create_article(
        self, url: str, publisher: str, session: AsyncSession
    ) -> CrawledArticle:
        return await CrawledArticleRepository().create(
            article=CrawledArticle(
                url=url,
                title="테스트입니당",
                content="테스트입니다",
                publisher=find_publisher(publisher).name,
            ),
            session=session,
        )

    async def get_article_by_id(
        self, article_id: int, session: AsyncSession
    ) -> CrawledArticle:
        return await CrawledArticleRepository().get(pk=article_id, session=session)

    async def get_all_articles(self, session: AsyncSession) -> List[CrawledArticle]:
        return await CrawledArticleRepository().get_all(session=session)
