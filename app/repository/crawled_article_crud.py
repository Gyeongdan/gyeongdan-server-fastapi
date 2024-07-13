from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import get_repository, model_to_dict
from app.model.crawled_article import Articles


class CrawledArticleRepository:
    async def create(self, article: Articles, session: AsyncSession):
        repository = get_repository(Articles)(session)
        return await repository.create(model_to_dict(article))

    async def get(self, pk: int, session: AsyncSession):
        repository = get_repository(Articles)(session)
        article = await repository.get(pk)
        if article is None:
            raise HTTPException(
                status_code=404, detail="해당 article이 존재하지 않습니다."
            )
        return article

    async def set_interest_type(
            self, pk:int, interest_types : List[int], session: AsyncSession
    ):
        repository = get_repository(Articles)(session)
        return await repository.update_by_pk(
            pk = pk,
            data = {
                'probability_issue_finder': interest_types[0],
                'probability_lifestyle_consumer': interest_types[1],
                'probability_entertainer': interest_types[2],
                'probability_tech_specialist': interest_types[3],
                'probability_professionals': interest_types[4]
            }

        )

    async def get_all(self, session: AsyncSession):
        repository = get_repository(Articles)(session)
        return await repository.filter()

    async def update_simplified_content(
        self, id: int, simplified_content: str, session: AsyncSession
    ):
        repository = get_repository(Articles)(session)
        return await repository.update_by_pk(
            pk=id, data={"simplified_content": simplified_content}
        )
