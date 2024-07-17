# api_visualization_router.py

from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.service.api_visualization_service import (
    ApiVisualizationService,
    create_article,
)
from app.utils.generic_response import GenericResponseDTO

api_visualization_router = APIRouter()


class select_data(Enum):
    population = "인구"
    childhood = "청소년 정책"
    JINJU = "진주 코비드"


class ApiVisualResponseDTO(BaseModel):
    title: str
    content: str
    html_data: str
    create_at: datetime


# 대충 이렇게 해놓고 모델 이런 거 만들어야 겠다.
@api_visualization_router.post(
    "/api_visual/article/{user_input}",
    response_model=GenericResponseDTO[ApiVisualResponseDTO],
)
async def api_visualization_article(
    user_input: bool,
    title: str,
    data_set: select_data,
    session: AsyncSession = Depends(get_db_session),
):
    # 지금 api 에서 고른다고 가정
    html_data, content = await create_article(
        title=title, data=data_set.value, user_input=user_input, session=session
    )

    if content == "":
        content = "user_input"

    return GenericResponseDTO[ApiVisualResponseDTO](
        data=ApiVisualResponseDTO(title=title, content=content, html_data=html_data),
        message="Successfully created article done.",
        result=True,
    )


@api_visualization_router.get(
    "/api_visual/article/{id}", response_model=GenericResponseDTO[ApiVisualResponseDTO]
)
async def get_api_visualization_article(
    id: int,
    session: AsyncSession = Depends(get_db_session),
):
    data = await ApiVisualizationService().get_by_id(id=id, session=session)
    return GenericResponseDTO[ApiVisualResponseDTO](
        data=ApiVisualResponseDTO(
            title=data.title,
            content=data.content,
            html_data=data.graph_html,
            create_at=data.create_at,
        ),
        message="Successfully 'get' done.",
        result=True,
    )
