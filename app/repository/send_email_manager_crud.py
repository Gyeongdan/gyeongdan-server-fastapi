# send_email_manager_crud.py
# DB crud 구현


from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# 여기는 나중에 제거할 생각
from app.database.repository import get_repository, model_to_dict
from app.model.send_email_manager import SendEmailManager


# 너무 길면 수정. create 만 만들고 적용해보자.
class SendEmailManagerRepository:
    async def create(self, email_manager: SendEmailManager, session: AsyncSession):
        repository = get_repository(SendEmailManager)(session)
        return await repository.create(model_to_dict(email_manager))
