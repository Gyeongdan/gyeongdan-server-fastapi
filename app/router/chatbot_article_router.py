from fastapi import APIRouter, Depends
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.service.chatbot_article_service import request_rag_applied_openai
from app.utils.generic_response import GenericResponseDTO

chatbot_article_router = APIRouter()

# 사용자 요청
class GenerateDetailArticleRequestDTO(BaseModel):
    id : int
    prompt: str


@chatbot_article_router.post(
    "/chatbot/article", response_model=GenericResponseDTO
)
async def chatbot_article_detail_(
        request: GenerateDetailArticleRequestDTO,
        session: AsyncSession = Depends(get_db_session)
):
    rag_applied_result = await request_rag_applied_openai(
        news_id =request.id,
        system_prompt=request.prompt,
        session = session
    )

    return GenericResponseDTO(
        result=True, data=rag_applied_result, message="Related articles found successfully."
    )

