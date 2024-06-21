from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.service.crawled_article_service import ArticleService

articles_router = APIRouter()


class ArticleCreateRequestDTO(BaseModel):
    url: str
    publisher: str


@articles_router.post("/articles")
async def create_article(
    dto: ArticleCreateRequestDTO, session: AsyncSession = Depends(get_db_session)
):
    return await ArticleService().create_article(dto.url, dto.publisher, session)


#
# def get_article_service(repo: DatabaseRepository[CrawledArticle] = Depends(
#     get_repository(CrawledArticle))) -> ArticleService:
#     return ArticleService(repo)
#
#
# # 1. Create a new article
# @router.post("/articles", response_model=CrawledArticleSchema,
#              status_code=status.HTTP_201_CREATED)
# async def create_article(
#     article: CrawledArticleCreate,
#     service: ArticleService = Depends(get_article_service)
# ):
#     try:
#         return await service.create_article(article)
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
#
#
# # 2. READ articles
# @router.get("/articles", response_model=list[CrawledArticleSchema],
#             status_code=status.HTTP_200_OK)
# async def read_all_articles(
#     service: ArticleService = Depends(get_article_service)
# ):
#     try:
#         return await service.get_all_articles()
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Unexpected error")
#
#
# @router.get("/articles/{article_id}", response_model=CrawledArticleSchema,
#             status_code=status.HTTP_200_OK)
# async def read_article_by_id(
#     article_id: int,
#     service: ArticleService = Depends(get_article_service)
# ):
#     try:
#         article = await service.get_article_by_id(article_id)
#         if article is None:
#             raise HTTPException(status_code=404, detail="Article not found")
#         return article
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
#
#
# # Update an article by ID
# @router.put("/articles/{id}", response_model=CrawledArticleSchema,
#             status_code=status.HTTP_200_OK)
# async def update_article(
#     id: int,
#     article: CrawledArticleUpdate,
#     service: ArticleService = Depends(get_article_service)
# ):
#     try:
#         updated_article = await service.update_article(id, article)
#         if updated_article is None:
#             raise HTTPException(status_code=404, detail="Article not found")
#         return updated_article
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
#
#
# # Delete an article by ID
# @router.delete("/articles/{id}", response_model=None,
#                status_code=status.HTTP_204_NO_CONTENT)
# async def delete_article(
#     id: int,
#     service: ArticleService = Depends(get_article_service)
# ):
#     try:
#         await service.delete_article(id)
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
