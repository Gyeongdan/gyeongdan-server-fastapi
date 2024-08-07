from typing import List

from fastapi import APIRouter, Depends
from groq import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.model.user_type import UserTypePercent
from app.recommend.recommend_service import user_type_to_classification_id
from app.repository.crawled_article_crud import CrawledArticleRepository
from app.repository.recommend_crud import RecommendRepository
from app.service.user_type_service import (
    UserTypeQuestionnaire,
    UserTypeQuestionnaireRequestDTO,
    UserTypeService,
    calculate_user_type,
)
from app.utils.generic_response import GenericResponseDTO

user_type_router = APIRouter()


class ArticleResponseDTO(BaseModel):
    id: int
    title: str
    content: str
    pubDate: str
    image: str


class UserTypeResponseDTO(BaseModel):
    percent: UserTypePercent
    userType: str
    recommendNews: List[ArticleResponseDTO]


@user_type_router.get(
    "/usertype/form",
    response_model=GenericResponseDTO[List[UserTypeQuestionnaire]],
)
async def get_questionnaire():
    data = await UserTypeService().get_questionnaire()
    return GenericResponseDTO[List[UserTypeQuestionnaire]](
        data=data, message="유형검사 질문지 조회에 성공", result=True
    )


@user_type_router.post(
    "/usertype/calculate", response_model=GenericResponseDTO[UserTypeResponseDTO]
)
async def create_user_type_by_answers(
    request: UserTypeQuestionnaireRequestDTO,
    session: AsyncSession = Depends(get_db_session),
):
    userType = calculate_user_type(request, UserTypeService().get_questionnaire_data())
    recommendNew_ids = await RecommendRepository().get(
        pk=await user_type_to_classification_id(userType), session=session
    )
    recommendNew_ids = recommendNew_ids.recommend_article_ids
    recommendNews = []

    for id in recommendNew_ids:
        temp_article = await CrawledArticleRepository().get(pk=id, session=session)
        recommendNews.append(
            ArticleResponseDTO(
                id=id,
                title=temp_article.simple_title,
                content=temp_article.simple_content,
                pubDate=temp_article.published_at.strftime("%Y-%m-%d"),
                image=temp_article.image_url,
            )
        )

    percent = UserTypePercent(
        issueFinder=userType[0],
        lifestyleConsumer=userType[1],
        entertainer=userType[2],
        techSpecialist=userType[3],
        professionals=userType[4],
    )

    return GenericResponseDTO[UserTypeResponseDTO](
        data=UserTypeResponseDTO(
            percent=percent,
            recommendNews=recommendNews,
            userType=percent.get_dominant_type(),
        ),
        message="유형검사 결과가 성공",
        result=True,
    )
