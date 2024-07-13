from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.article_publisher import Publisher
from app.model.crawled_article import Articles
from app.model.subscription import MailTypeCategory
from app.repository.crawled_article_crud import CrawledArticleRepository

class ArticleManageService:
    async def create_article(
        self,
        url: str,
        publisher: Publisher,
        title: str,
        content: str,
        simple_title: str,
        simple_content: str,
        phrase: dict,
        comment: str,
        category: MailTypeCategory,
        session: AsyncSession,
    ) -> Articles:
        return await CrawledArticleRepository().create(
            article=Articles(
                url=url,
                title=title,
                content=content,
                publisher=publisher.name,
                simple_title=simple_title,
                simple_content=simple_content,
                comment=comment,
                category=category.name,
                phrase=phrase,
                probability_issue_finder=-1
            ),
            session=session,
        )

    async def update_simplified_article(
        self, id: int, simplified_content: str, session: AsyncSession
    ) -> Articles:
        return await CrawledArticleRepository().update_simplified_content(
            id=id, simplified_content=simplified_content, session=session
        )

    async def get_article_by_id(
        self, article_id: int, session: AsyncSession
    ) -> Articles:
        return await CrawledArticleRepository().get(pk=article_id, session=session)

    async def get_all_articles(self, session: AsyncSession) -> List[Articles]:
        return await CrawledArticleRepository().get_all(session=session)
