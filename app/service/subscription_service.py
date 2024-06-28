from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.subscription import Subscription
from app.repository.subscription_crud import SubscriptionRepository

from fastapi import HTTPException

import re

async def validate_email_address(email_address: str):
    pattern = '^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(pattern, email_address):
        raise HTTPException(
            status_code=422, detail="email-address의 양식이 올바르지 않습니다."
        )

class SubscriptionService:
    async def create_subscription(
        self, name: str, email_address: str, category: int , session: AsyncSession
    ) -> Subscription:
        await validate_email_address(email_address)
        return await SubscriptionRepository().create(
            subscription=Subscription(
                name= name,
                email_address=email_address,
                category=category,
                status=True,
            ),
            session=session,
        )



    async def get_subscription_by_id(
        self, id: int, session: AsyncSession
    ) -> Subscription:
        return await SubscriptionRepository().get(pk=id, session=session)

    async def update_status(self, id: int, status:bool, session:AsyncSession) -> Subscription:
        return await SubscriptionRepository().update_status(
            id=id, status=status, session=session
        )

    async  def update_category(self, id: int, category: int, session:AsyncSession) -> Subscription:
        return await SubscriptionRepository().update_category(
            id=id, category=category, session=session
        )

    async def get_active_subcriptions_by_category(self, category: int, session:AsyncSession) -> List[Subscription]:
        return await SubscriptionRepository().get_active_subscriptions_by_category(category=category, session=session)

    async def get_all_subcriptions(self, session: AsyncSession) -> List[Subscription]:
        return await SubscriptionRepository().get_all(session=session)
