from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.service.user_type_service import (
    UserTypeQuestionnaire,
    UserTypeQuestionnaireRequestDTO,
    UserTypeService,
)
from app.utils.generic_response import GenericResponseDTO

user_type_router = APIRouter()


@user_type_router.get(
    "/user-type/questionnaire",
    response_model=GenericResponseDTO[List[UserTypeQuestionnaire]],
)
async def get_questionnaire():
    data = await UserTypeService().get_questionnaire()
    return GenericResponseDTO[List[UserTypeQuestionnaire]](
        data=data, message="Questionnaire retrieved successfully", result=True
    )


@user_type_router.post("/user-type", response_model=GenericResponseDTO[int])
async def create_subscription(
    request: UserTypeQuestionnaireRequestDTO,
    session: AsyncSession = Depends(get_db_session),
):
    await UserTypeService().create_user_type(request, session)
    return GenericResponseDTO[int](
        data=request.id, message="user type created successfully", result=True
    )
