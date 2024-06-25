from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.service.subscription_service import SubscriptionService

subscription_router = APIRouter()

class SubcriptionCreateRequestDTO(BaseModel):
    name : str
    emailAddress : str
    category : int

@subscription_router.post("/subscriptions/save")
async def create_subscription(
    name :str, email_address:str, category: int , session: AsyncSession = Depends(get_db_session)
):
    return await SubscriptionService().create_subscription(name, email_address, category, session)

@subscription_router.get("/subscriptions/{id}")
async def get_subscription_by_id(id: int, session: AsyncSession = Depends(get_db_session)):
    return await SubscriptionService().get_subscription_by_id(id, session)

@subscription_router.post("/subscriptions/{id}/status")
async def update_status(id:int, status:bool, session: AsyncSession = Depends(get_db_session)):
    return await SubscriptionService().update_status(id, status, session)

@subscription_router.get("/subscriptions/category/{category}")
async def get_active_subscriptions_by_category(category: int, session: AsyncSession = Depends(get_db_session)):
    return await SubscriptionService().get_active_subcriptions_by_category(category, session)

@subscription_router.post("/subscriptions/{id}/category")
async def update_category(id:int, category:int, session:AsyncSession = Depends(get_db_session)):
    return await SubscriptionService().update_category(id, category, session)

@subscription_router.get("/subscriptions")
async def get_all_subscriptions(session: AsyncSession = Depends(get_db_session)):
    return await SubscriptionService().get_all_subcriptions(session)
