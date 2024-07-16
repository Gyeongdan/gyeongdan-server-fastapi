from enum import Enum

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.service.api_visualization_service import (
    ApiVisualizationService,
    create_article,
)

api_visualization_router = APIRouter()


class select_data(Enum):
    population = "인구"
    childhood = "청소년 정책"
    JINJU = "진주 코비드"


# 대충 이렇게 해놓고 모델 이런 거 만들어야 겠다.
@api_visualization_router.post("/api_visual/article/{user_input}")
async def api_visualization_article(
    user_input: bool,
    title: str,
    data_set: select_data,
    session: AsyncSession = Depends(get_db_session),
):
    # 지금 api 에서 고른다고 가정
    await create_article(
        title=title, data=data_set.value, user_input=user_input, session=session
    )

    return "Great JOB"


@api_visualization_router.get("/api_visual/article/{id}")
async def get_api_visualization_article(
    id: int,
    session: AsyncSession = Depends(get_db_session),
):
    return await ApiVisualizationService().get_by_id(id=id, session=session)
