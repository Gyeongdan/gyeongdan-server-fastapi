# send_email_manager_crud_router.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.service.send_email_manager_service import ManagerService

email_manager_router = APIRouter()


class ManagerCreateRequestDTO(BaseModel):
    category: int
    content: str


@email_manager_router.post('/send_email_manager/save')
async def create_manager(
        category: int, content: str, session: AsyncSession = Depends(get_db_session)
):
    return await ManagerService().create_manager(category, content, session)

