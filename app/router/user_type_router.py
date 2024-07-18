from typing import List, Dict

from fastapi import APIRouter, Depends
from groq import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import model_to_dict
from app.database.session import get_db_session
from app.model.user_type import UserType
from app.recommend.recommend_service import RecommendService, user_id_to_classification_id, \
    user_type_to_classification_id
from app.repository.crawled_article_crud import CrawledArticleRepository
from app.repository.recommend_crud import RecommendRepository
from app.service.user_type_service import (
    UserTypeQuestionnaire,
    UserTypeQuestionnaireRequestDTO,
    UserTypeService, calculate_user_type,
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
    userType: Dict
    recommendNews: List[ArticleResponseDTO]



@user_type_router.get(
    "/user-type/questionnaire",
    response_model=GenericResponseDTO[List[UserTypeQuestionnaire]],
)
async def get_questionnaire():
    data = await UserTypeService().get_questionnaire()
    return GenericResponseDTO[List[UserTypeQuestionnaire]](
        data=data, message="Questionnaire retrieved successfully", result=True
    )


@user_type_router.post("/user-type", response_model=GenericResponseDTO[UserTypeResponseDTO])
async def create_user_type_by_answers(
    request: UserTypeQuestionnaireRequestDTO,
    session: AsyncSession = Depends(get_db_session),
):
    recommendNew_ids = []
    if request.id == None:
        userType = calculate_user_type(
            request, UserTypeService().get_questionnaire_data()
        )
        recommendNew_ids = await RecommendRepository().get(
            pk=await user_type_to_classification_id(userType),
            session=session)
        recommendNew_ids = recommendNew_ids.recommend_article_ids
    else :
        userType = await UserTypeService().create_user_type(request, session)
        recommendNew_ids = await RecommendRepository().get(
            pk=await user_id_to_classification_id(user_id=userType.user_id, session=session),
            session=session)
        recommendNew_ids = recommendNew_ids.recommend_article_ids
    recommendNews = []

    for id in recommendNew_ids:
        temp_article = await CrawledArticleRepository().get(pk=id, session=session)
        recommendNews.append(ArticleResponseDTO(
            id=id,
            title=temp_article.simple_title,
            content=temp_article.simple_content,
            pubDate=temp_article.published_at.strftime("%Y-%m-%d"),
            image=temp_article.image_url
        ))
    if request.id == None:
        return GenericResponseDTO[UserTypeResponseDTO](
            data=UserTypeResponseDTO(
                userType={'ISSUE_FINDER': userType[0],
                          'LIFESTYLE_CONSUMER': userType[1],
                          'ENTERTAINER': userType[2],
                          'TECH_SPECIALIST': userType[3],
                          'PROFESSIONALS': userType[4]},
                recommendNews=recommendNews
            ), message="user type created successfully", result=True
        )
    else:
        return GenericResponseDTO[UserTypeResponseDTO](
            data=UserTypeResponseDTO(
                userType={'ISSUE_FINDER': userType.user_type_issue_finder,
                          'LIFESTYLE_CONSUMER': userType.user_type_lifestyle_consumer,
                          'ENTERTAINER': userType.user_type_entertainer,
                          'TECH_SPECIALIST': userType.user_type_tech_specialist,
                          'PROFESSIONALS': userType.user_type_professionals},
                recommendNews=recommendNews
            ), message="user type created successfully", result=True
        )
