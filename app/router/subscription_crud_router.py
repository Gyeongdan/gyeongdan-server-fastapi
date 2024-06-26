from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.database.session import get_db_session
from app.service.subscription_service import SubscriptionService
from app.utils.generic_response import GenericResponseDTO
from app.model.subscription import Subscription

subscription_router = APIRouter()

class SubcriptionResponseDTO(BaseModel):
    name : str
    email_address : str
    category : int
    status : bool

def subcription_to_subscriptionResponseDTO(subscription : Subscription) :
    return SubcriptionResponseDTO(
        name=subscription.name,
        email_address=subscription.email_address,
        category=subscription.category,
        status=subscription.status
    )

def subcription_list_to_subscriptionResponseDTO_list(subscriptions : List[Subscription]) :
    return list(map(subcription_to_subscriptionResponseDTO, subscriptions))

@subscription_router.post("/subscriptions/save", response_model=GenericResponseDTO[int])
async def create_subscription(
    name :str, email_address:str, category: int , session: AsyncSession = Depends(get_db_session)
):
    subscription = await SubscriptionService().create_subscription(name, email_address, category, session)
    return GenericResponseDTO[int](
        data=subscription.id,
        message="Subscription created successfully",
        result=True
    )

@subscription_router.get("/subscriptions/{id}", response_model=GenericResponseDTO[SubcriptionResponseDTO])
async def get_subscription_by_id(id: int, session: AsyncSession = Depends(get_db_session)):
    subscription = await SubscriptionService().get_subscription_by_id(id, session)
    return GenericResponseDTO[SubcriptionResponseDTO](
        data=subcription_to_subscriptionResponseDTO(subscription),
        message="Subscription retrieved successfully",
        result=True
    )

@subscription_router.post("/subscriptions/{id}/status", response_model=GenericResponseDTO[SubcriptionResponseDTO])
async def update_status(id:int, status:bool, session: AsyncSession = Depends(get_db_session)):
    subscription =  await SubscriptionService().update_status(id, status, session)
    return GenericResponseDTO[SubcriptionResponseDTO](
            data=subcription_to_subscriptionResponseDTO(subscription),
            message="Subscription Status Updated successfully",
            result=True
        )

@subscription_router.get("/subscriptions/category/{category}", response_model=GenericResponseDTO[List[SubcriptionResponseDTO]])
async def get_active_subscriptions_by_category(category: int, session: AsyncSession = Depends(get_db_session)):
    subscriptions = await SubscriptionService().get_active_subcriptions_by_category(category, session)
    return GenericResponseDTO[List[SubcriptionResponseDTO]](
        data= subcription_list_to_subscriptionResponseDTO_list(subscriptions),
        message="Subscriptions retrieved successfully",
        result=True
    )

@subscription_router.post("/subscriptions/{id}/category", response_model=GenericResponseDTO[SubcriptionResponseDTO])
async def update_category(id:int, category:int, session:AsyncSession = Depends(get_db_session)):
    subscription = await SubscriptionService().update_category(id, category, session)
    return GenericResponseDTO[SubcriptionResponseDTO](
        data=subcription_to_subscriptionResponseDTO(subscription),
        message="Subscription Category Updated successfully",
        result=True
    )

@subscription_router.get("/subscriptions", response_model=GenericResponseDTO[List[SubcriptionResponseDTO]])
async def get_all_subscriptions(session: AsyncSession = Depends(get_db_session)):
    subscriptions = await SubscriptionService().get_all_subcriptions(session)
    return GenericResponseDTO[List[SubcriptionResponseDTO]](
        data= subcription_list_to_subscriptionResponseDTO_list(subscriptions),
        message="Subscriptions retrieved successfully",
        result=True
    )
