from fastapi import APIRouter, Depends, HTTPException, status
from app.database.repository import DatabaseRepository, get_repository
from app.model.crawled_article_model import CrawledArticle, NewspaperEnum
from app.model.crawled_article_schema import CrawledArticle as CrawledArticleSchema, CrawledArticleCreate, \
    CrawledArticleUpdate

router = APIRouter()

# 1. Create Article
@router.post("/articles", response_model=CrawledArticleSchema, status_code=status.HTTP_201_CREATED)
async def create_article(
        article: CrawledArticleCreate,
        repo: DatabaseRepository[CrawledArticle] = Depends(get_repository(CrawledArticle))
):
    try:
        article_dict = article.dict()
        article_dict['newspaper'] = article_dict['newspaper'].name  # Enum을 문자열로 변환
        created_article = await repo.create(article_dict)
        return created_article
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 2. Read Articles
@router.get("/articles", response_model=list[CrawledArticleSchema])
async def read_all_articles(
        repo: DatabaseRepository[CrawledArticle] = Depends(get_repository(CrawledArticle))
):
    articles = await repo.filter()
    return articles


@router.get("/articles/{article_id}", response_model=CrawledArticleSchema)
async def read_article(
        article_id: int,
        repo: DatabaseRepository[CrawledArticle] = Depends(get_repository(CrawledArticle))
):
    article = await repo.get(article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    # newspaper를 Enum으로 변환
    article.newspaper = NewspaperEnum[article.newspaper]
    return article

# 3. Update Article
@router.put("/articles/{article_id}", response_model=CrawledArticleSchema)
async def update_article(
        article_id: int,
        article: CrawledArticleUpdate,
        repo: DatabaseRepository[CrawledArticle] = Depends(get_repository(CrawledArticle))
):
    existing_article = await repo.get(article_id)
    if existing_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    updated_article = await repo.update_by_pk(article_id, article.dict(exclude_unset=True))
    return updated_article

# 4. Delete Article
@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
        article_id: int,
        repo: DatabaseRepository[CrawledArticle] = Depends(get_repository(CrawledArticle))
):
    article = await repo.get(article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await repo.delete(article_id)
    return None
