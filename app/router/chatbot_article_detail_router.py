from fastapi import APIRouter
from pydantic import BaseModel

from app.service.chatbot_article_detail_service import request_rag_applied_openai
from app.utils.generic_response import GenericResponseDTO

chatbot_article_router = APIRouter()

# 사용자 요청
class GenerateDetailArticleRequestDTO(BaseModel):
    news_content: str
    prompt: str


@chatbot_article_router.post(
    "/chatbot-article-detail", response_model=GenericResponseDTO
)
async def chatbot_article_detail_(
        request: GenerateDetailArticleRequestDTO,
):
    rag_applied_result = await request_rag_applied_openai(
        original_text=request.news_content,
        system_prompt=request.prompt
    )

    return GenericResponseDTO(
        result=True, data=rag_applied_result, message="Related articles found successfully."
    )

