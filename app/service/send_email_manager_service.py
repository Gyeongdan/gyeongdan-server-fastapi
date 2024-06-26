# send_email_manager_service.py

from typing import List
from sqlalchemy import SmallInteger
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.send_email_manager import SendEmailManager
from app.repository.send_email_manager_crud import SendEmailManagerRepository


class ManagerService:
    async def create_manager(
            self, category: int, content: str, session: AsyncSession
    ) -> SendEmailManager:
        return await SendEmailManagerRepository().create(
            email_manager=SendEmailManager(
                category=category,
                content=content
            ),
            session=session
        )

# json 형식으로 반환
    async def get_content_by_id(
            self, id: int, session: AsyncSession
    ) -> SendEmailManager:
        return await SendEmailManagerRepository().get_by_id(pk=id, session=session)

    async def get_all_contents(self, session: AsyncSession) -> List[SendEmailManager]:
        return await SendEmailManagerRepository().get_all(session=session)

    async def get_content_by_category(self, category: int, session: AsyncSession) -> List[SendEmailManager]:
        return await SendEmailManagerRepository().get_by_category(category=category, session=session)
