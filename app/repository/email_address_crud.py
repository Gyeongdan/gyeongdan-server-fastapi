from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import get_repository, model_to_dict
from app.model.email_address import EmailAddress


class EmailAddressRepository:
    async def create(self, address: EmailAddress, session: AsyncSession):
        repository = get_repository(EmailAddress)(session)
        return await repository.create(model_to_dict(address))

    async def get(self, pk: int, session: AsyncSession):
        repository = get_repository(EmailAddress)(session)
        address = await repository.get(pk)
        if address is None:
            raise HTTPException(
                status_code=404, detail="해당 email-address이 존재하지 않습니다."
            )
        return address

    async def get_all(self, session: AsyncSession):
        repository = get_repository(EmailAddress)(session)
        return await repository.filter()