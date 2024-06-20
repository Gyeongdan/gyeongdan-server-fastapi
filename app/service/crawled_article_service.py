from typing import List, Optional
from app.model.crawled_article_model import CrawledArticle, CrawledArticleCreate, CrawledArticleUpdate, \
    CrawledArticleSchema
from app.database.repository import DatabaseRepository

class ArticleService:
    def __init__(self, repo: DatabaseRepository[CrawledArticle]):
        self.repo = repo

    async def create_article(self, article_data: CrawledArticleCreate) -> CrawledArticle:
        article_dict = article_data.dict()
        article_dict['newspaper'] = article_dict['newspaper'].value  # Enum to string conversion
        return await self.repo.create(article_dict)

    async def get_article_by_id(self, article_id: int) -> Optional[CrawledArticle]:
        article = await self.repo.get(article_id)
        if article:
            article.newspaper = article.newspaper.value  # Enum to string conversion
        return article

    async def get_all_articles(self) -> List[CrawledArticle]:
        articles = await self.repo.filter()
        for article in articles:
            article.newspaper = article.newspaper.value  # Enum to string conversion
        return articles

    async def update_article(self, article_id: int, article_data: CrawledArticleUpdate) -> Optional[CrawledArticle]:
        article_dict = article_data.dict(exclude_unset=True)
        if 'newspaper' in article_dict and article_dict['newspaper']:
            article_dict['newspaper'] = article_dict['newspaper'].value  # Enum to string conversion
        return await self.repo.update_by_pk(article_id, article_dict)

    async def delete_article(self, article_id: int) -> None:
        await self.repo.delete(article_id)
