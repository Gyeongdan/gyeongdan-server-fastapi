from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.article_publisher import find_publisher
from app.model.email_address import EmailAddress
from app.repository.email_address_crud import EmailAddressRepository


class AddressService:
    async def create_address(
        self, address: str, name: str, session: AsyncSession
    ) -> EmailAddress:
        return await EmailAddressRepository().create(
            article=EmailAddress(
                emailAddress= address,
                name= name,
                valid=True,
            ),
            session=session,
        )


    async def get_user_data_by_id(
        self, article_id: int, session: AsyncSession
    ) -> EmailAddress:
        return await EmailAddressRepository().get(pk=article_id, session=session)

    async def get_all_user_datas(self, session: AsyncSession) -> List[EmailAddress]:
        return await EmailAddressRepository().get_all(session=session)
