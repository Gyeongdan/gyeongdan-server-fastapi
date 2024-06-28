from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import get_repository, model_to_dict
from app.model.subscription import MailTypeCategory, Subscription


class SubscriptionRepository:
    async def create(self, subscription: Subscription, session: AsyncSession):
        repository = get_repository(Subscription)(session)
        return await repository.create(model_to_dict(subscription))

    async def get(self, pk: int, session: AsyncSession):
        repository = get_repository(Subscription)(session)
        subscription = await repository.get(pk)
        if subscription is None:
            raise HTTPException(
                status_code=404, detail="해당 email-address이 존재하지 않습니다."
            )
        return subscription

    async def update_category(
        self, id: int, category: MailTypeCategory, session: AsyncSession
    ):
        repository = get_repository(Subscription)(session)
        return await repository.update_by_pk(pk=id, data={"category": category.name})

    async def update_status(self, id: int, status: bool, session: AsyncSession):
        repository = get_repository(Subscription)(session)
        return await repository.update_by_pk(pk=id, data={"status": status})

    async def get_active_subscriptions_by_category(
        self, category: MailTypeCategory, session: AsyncSession
    ):
        repository = get_repository(Subscription)(session)
        return await repository.filter(
            and_(Subscription.status, Subscription.category == category.name)
        )

    async def get_all(self, session: AsyncSession):
        repository = get_repository(Subscription)(session)
        return await repository.filter()
