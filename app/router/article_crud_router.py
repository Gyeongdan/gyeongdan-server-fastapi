from fastapi import APIRouter, Depends, HTTPException, status
from app.model.crawled_article_model import CrawledArticle, CrawledArticleCreate, CrawledArticleUpdate, \
    CrawledArticleSchema, CrawledArticleBase
from app.database.repository import DatabaseRepository, get_repository

router = APIRouter()

# 1. Create a new article
@router.post("/articles", response_model=CrawledArticleSchema, status_code=status.HTTP_201_CREATED)
async def create_article(
    article: CrawledArticleBase,
    repo: DatabaseRepository[CrawledArticle] = Depends(get_repository(CrawledArticle))
):
    try:
        article_dict = article.dict()
        article_dict['newspaper'] = article_dict['newspaper'].value  # Enum을 문자열로 변환
        print("Article Dictionary: ", article_dict)  # 디버깅용으로 출력
        created_article = await repo.create(article_dict)
        return created_article
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 2. READ articles
# read_all_articles
@router.get("/articles", response_model=list[CrawledArticleSchema], status_code=status.HTTP_200_OK)
async def read_all_articles(
    repo: DatabaseRepository[CrawledArticle] = Depends(get_repository(CrawledArticle))
):
    try:
        articles = await repo.filter()
        for article in articles:
            # Enum을 문자열로 변환
            article.newspaper = article.newspaper.value
        return articles
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")

# read_article_by_id
@router.get("/articles/{article_id}", response_model=CrawledArticleSchema, status_code=status.HTTP_200_OK)
async def read_article_by_id(
    article_id: int,
    repo: DatabaseRepository[CrawledArticle] = Depends(get_repository(CrawledArticle))
):
    try:
        article = await repo.get(article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Article not found")

        article.newspaper = article.newspaper.value  # Convert Enum to string
        return article
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Update an article by ID
@router.put("/articles/{id}", response_model=CrawledArticleSchema, status_code=status.HTTP_200_OK)
async def update_article(
    id: int,
    article: CrawledArticleUpdate,
    repo: DatabaseRepository[CrawledArticle] = Depends(get_repository(CrawledArticle))
):
    article_dict = article.dict(exclude_unset=True)
    if 'newspaper' in article_dict and article_dict['newspaper']:
        article_dict['newspaper'] = article_dict['newspaper'].value  # Enum to string conversion
    updated_article = await repo.update_by_pk(id, article_dict)
    if updated_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated_article

# Delete an article by ID
@router.delete("/articles/{id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    id: int,
    repo: DatabaseRepository[CrawledArticle] = Depends(get_repository(CrawledArticle))
):
    article = await repo.get(id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await repo.delete(id)
