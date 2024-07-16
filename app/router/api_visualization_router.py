from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.service.api_visualization_service import create_article
from app.service.public_data_api_service import PublicDataAPI

api_visualization_router = APIRouter()


# 대충 이렇게 해놓고 모델 이런 거 만들어야 겠다.
@api_visualization_router.post("/api_visual/article/{user_input}")
async def api_visualization_article(
    user_input: bool,
    title: str,
    data_set: PublicDataAPI,
    session: AsyncSession = Depends(get_db_session),
):
    # 지금 api 에서 고른다고 가정
    await create_article(
        title=title, data=data_set, user_input=user_input, session=session
    )

    return "잘 되너 듯"
