from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.article_publisher import find_publisher
from app.model.subscription import Subscription
from app.repository.subscription_crud import SubscriptionRepository


class SubscriptionService:
    async def create_subscription(
        self, name: str, address: str, category: int , session: AsyncSession
    ) -> Subscription:
        return await SubscriptionRepository().create(
            subscription=Subscription(
                name= name,
                email_address=address,
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
        return await SubscriptionRepository.update_status(
            id=id, status=status, session=session
        )

    async  def update_category(self, id: int, category: int, session:AsyncSession) -> Subscription:
        return await SubscriptionRepository.update_category(
            id=id, category=category, session=session
        )

    async def get_all_subcriptions(self, session: AsyncSession) -> List[Subscription]:
        return await SubscriptionRepository().get_all(session=session)
