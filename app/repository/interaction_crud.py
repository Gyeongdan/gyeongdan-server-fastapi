from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import get_repository, model_to_dict
from app.model.interaction import Interaction


class InteractionRepository:
    async def create(self, interaction: Interaction, session: AsyncSession):
        repository = get_repository(Interaction)(session)
        return await repository.create(model_to_dict(interaction))

    async def get_all(self, session: AsyncSession):
        repository = get_repository(Interaction)(session)
        return await repository.filter()