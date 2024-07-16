from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import get_repository
from app.model.recommend import Recommend

class RecommendRepository:
    async def update_recommend(
            self, id: int, article_ids: List[int], session: AsyncSession
    ):
        repository = get_repository(Recommend)(session)
        return await repository.update_by_pk(
            pk=id,
            data={
                "recommend_article_ids": article_ids
            },
        )