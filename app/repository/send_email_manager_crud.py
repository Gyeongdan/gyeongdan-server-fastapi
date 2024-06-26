# send_email_manager_crud.py
# DB crud 구현


from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 여기는 나중에 제거할 생각
from app.database.repository import get_repository, model_to_dict
from app.model.send_email_manager import SendEmailManager


# 너무 길면 수정. create 만 만들고 적용해보자.
class SendEmailManagerRepository:
    async def create(self, email_manager: SendEmailManager, session: AsyncSession):
        repository = get_repository(SendEmailManager)(session)
        return await repository.create(model_to_dict(email_manager))

    async def get_by_id(self, pk: int, session: AsyncSession):
        repository = get_repository(SendEmailManager)(session)
        content = await repository.get(pk)
        if content is None:
            raise HTTPException(
                status_code=404, detail="해당 순번이 존재하지 않습니다."
            )
        return content

    async def get_all(self, session: AsyncSession):
        repository = get_repository(SendEmailManager)(session)
        return await repository.filter()

    async def get_by_category(
            self, category: int, session: AsyncSession
    ):
        result = await session.execute(
            select(SendEmailManager).where(SendEmailManager.category == category)
        )
        return result.scalars().all()
