from sqlalchemy.ext.asyncio import AsyncSession
from app.model.article_related_document import ArticleRelatedDocument

class ArticleRelatedDocumentService:
    async def save(
            self, article_id: int, document: dict, session: AsyncSession
    ) -> ArticleRelatedDocument:
        related_document: ArticleRelatedDocument = ArticleRelatedDocument(
            article_id=article_id,
            title=document.get("title"),
            link=document.get("link"),
            snippet=document.get("snippet")
        )

        session.add(related_document)
        await session.commit()
        await session.refresh(related_document)

        return related_document
