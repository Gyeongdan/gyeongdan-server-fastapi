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

@email_manager_router.get('/send_email_manager/{id}')
async def get_content_by_id(id: int, session: AsyncSession = Depends(get_db_session)):
    return await ManagerService().get_content_by_id(id, session)

@email_manager_router.get('/send_email_manager')
async def get_all(session: AsyncSession = Depends(get_db_session)):
    return await ManagerService().get_all_contents(session)

@email_manager_router.get('/send_email_manager/search/{category}')
async def get_content_by_category(category: int, session: AsyncSession = Depends(get_db_session)):
    return await ManagerService().get_content_by_category(category, session)

@email_manager_router.put('/send_email_manager/update')
async def update_content_by_id(id: int, content: str, session: AsyncSession = Depends(get_db_session)):
    return await ManagerService().update_content(id, content, session)
