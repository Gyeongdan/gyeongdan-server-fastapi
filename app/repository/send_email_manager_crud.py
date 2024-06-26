# send_email_manager_crud.py
# DB crud 구현


from fastapi import HTTPException
from sqlalchemy import select, func
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

    # 기사 내용을 수정해야 할 때 사용
    # 추가로 업데이트 된 시간도 수정
    async def update_by_id(
            self, id: int, content: str, session: AsyncSession
    ):
        repository = get_repository(SendEmailManager)(session)
        return await repository.update_by_pk(
                pk=id, data={"content": content, "updated_at": func.now()}
        )
