from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import get_repository, model_to_dict
from app.model.user_type import UserType
from app.service.user_type_service import UserTypes


class UserTypeRepository:
    async def create(self, user_type: UserType, session: AsyncSession):
        repository = get_repository(UserType)(session)
        return await repository.create(model_to_dict(user_type))

    async def get(self, pk: int, session: AsyncSession):
        repository = get_repository(UserType)(session)
        user_type = await repository.get(pk)
        if user_type is None:
            raise HTTPException(status_code=404, detail="해당 유저가 없습니다.")
        return user_type

    async def update_user_type(
        self, id: int, user_types: List[int], session: AsyncSession
    ):
        repository = get_repository(UserType)(session)
        return await repository.update_by_pk(
            pk=id,
            data={
                "user_type_issue_finder": user_types[UserTypes.ISSUE_FINDER.value],
                "user_type_lifestyle_consumer": user_types[
                    UserTypes.LIFESTYLE_CONSUMER.value
                ],
                "user_type_entertainer": user_types[UserTypes.ENTERTAINER.value],
                "user_type_tech_specialist": user_types[
                    UserTypes.TECH_SEPCIALIST.value
                ],
                "user_type_professionals": user_types[UserTypes.PROFESSIONALS.value],
            },
        )

    async def get_all(self, session: AsyncSession):
        repository = get_repository(UserType)(session)
        return await repository.filter()
