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