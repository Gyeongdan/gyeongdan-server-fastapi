from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.service.article_manage_service import ArticleManageService

articles_router = APIRouter()


@articles_router.post("/articles/{id}/simplified-content")
async def update_simplified_content(
    id: int, simplified_content: str, session: AsyncSession = Depends(get_db_session)
):
    return await ArticleManageService().update_simplified_article(
        id=id, simplified_content=simplified_content, session=session
    )


@articles_router.get("/articles/{id}")
async def get_article_by_id(id: int, session: AsyncSession = Depends(get_db_session)):
    return await ArticleManageService().get_article_by_id(id, session)


@articles_router.get("/articles")
async def get_all_articles(session: AsyncSession = Depends(get_db_session)):
    return await ArticleManageService().get_all_articles(session)
