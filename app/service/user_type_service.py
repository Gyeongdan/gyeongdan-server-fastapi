from typing import List

from groq import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.user_type import UserType, UserTypes
from app.repository.user_type_crud import UserTypeRepository


class UserTypeQuestionnaireRequestDTO(BaseModel):
    id: int
    answers: List[int]


class QuestionnaireOption(BaseModel):
    option: str
    option_weight: int
    option_weight_pointer: int


class UserTypeQuestionnaire(BaseModel):
    title: str
    option1: QuestionnaireOption
    option2: QuestionnaireOption
    option3: QuestionnaireOption


def set_user_type_questionnaire(questionnaire_data) -> List[UserTypeQuestionnaire]:
    questionnaire_result = []
    for questionnaire in questionnaire_data:
        questionnaire_result.append(
            UserTypeQuestionnaire(
                title=questionnaire[0],
                option1=QuestionnaireOption(
                    option=questionnaire[1][0],
                    option_weight=questionnaire[1][1],
                    option_weight_pointer=questionnaire[1][2],
                ),
                option2=QuestionnaireOption(
                    option=questionnaire[2][0],
                    option_weight=questionnaire[2][1],
                    option_weight_pointer=questionnaire[2][2],
                ),
                option3=QuestionnaireOption(
                    option=questionnaire[3][0],
                    option_weight=questionnaire[3][1],
                    option_weight_pointer=questionnaire[3][2],
                ),
            )
        )
    return questionnaire_result


def calculate_user_type(answers: UserTypeQuestionnaireRequestDTO, questionnaire_data):
    user_type = [0 for _ in range(5)]
    for i in range(10):  # answer in answers.answers:
        answer_index = int(answers.answers[i])  # answers의 각 항목을 정수로 변환
        user_type_index = int(
            questionnaire_data[i][answer_index + 1][2]
        )  # 정수 인덱스로 접근
        if user_type_index == UserTypes.NONE:
            continue
        user_type[user_type_index] += questionnaire_data[i][answer_index + 1][1]
    return user_type


class UserTypeService:
    def __init__(self):
        self.questionnaire_data = [
            [
                "최신 경제 이슈에 대해 얼마나  잘 알고 있습니까?",
                ["매우 잘 알고 있다.", 10, UserTypes.ISSUE_FINDER.value],
                ["다소 알고 있다.", 5, UserTypes.ISSUE_FINDER.value],
                ["잘 모른다.", 0, UserTypes.NONE.value],
            ],
            [
                "경제 뉴스를 얼마나 자주 찾아보십니까?",
                ["매일 확인한다.", 10, UserTypes.ISSUE_FINDER.value],
                ["주간 단위로 확인한다.", 5, UserTypes.ISSUE_FINDER.value],
                ["가끔 확인한다.", 0, UserTypes.NONE.value],
            ],
            [
                "경제 관련 논란이나 논쟁에 얼마나 관심이 있습니까?",
                ["매우 관심이 있다.", 10, UserTypes.ISSUE_FINDER.value],
                ["다소 관심이 있다.", 5, UserTypes.ISSUE_FINDER.value],
                ["잘 모른다.", 0, UserTypes.NONE.value],
            ],
            [
                "경제 정보를 어떻게 활용하시나요?",
                ["일상 생활에 적용해본다.", 10, UserTypes.LIFESTYLE_CONSUMER.value],
                ["흥미로운 정보는 기억한다.", 10, UserTypes.ENTERTAINER.value],
                ["크게 활용하지 않는다.", 0, UserTypes.NONE.value],
            ],
            [
                "절약이나 소비자 팁에 관심이 있으신가요?",
                ["매우 관심이 있다.", 10, UserTypes.LIFESTYLE_CONSUMER.value],
                ["다소 관심이 있다.", 5, UserTypes.LIFESTYLE_CONSUMER.value],
                ["별로 관심이 없다.", 0, UserTypes.NONE.value],
            ],
            [
                "경제 관련 이야기를 어떻게 즐기시나요?",
                ["심도 깊게 분석한다.", 10, UserTypes.PROFESSIONALS.value],
                ["가벼운 마음으로 즐긴다.", 5, UserTypes.ENTERTAINER.value],
                ["별로 관심이 없다.", 0, UserTypes.NONE.value],
            ],
            [
                "기술과 경제의 결합에 대해 얼마나 잘 이해하고 있습니까?",
                ["매우 잘 이해한다.", 10, UserTypes.TECH_SEPCIALIST.value],
                ["다소 이해한다.", 5, UserTypes.TECH_SEPCIALIST.value],
                ["잘 모른다.", 0, UserTypes.NONE.value],
            ],
            [
                "기술 발전이 경제에 미치는 영향에 대해 얼마나 알고 있습니까?",
                ["깊이 있는 지식이 있다. ", 10, UserTypes.TECH_SEPCIALIST.value],
                ["일반적인 이해만 한다. ", 5, UserTypes.TECH_SEPCIALIST.value],
                ["잘 모른다.", 0, UserTypes.NONE.value],
            ],
            [
                "전문가 의견이나 통계 데이터에 관심이 있으신가요?",
                ["매우 관심이 있다.", 10, UserTypes.PROFESSIONALS.value],
                ["다소 관심이 있다.", 5, UserTypes.PROFESSIONALS.value],
                ["별로 관심이 없다. ", 5, UserTypes.ENTERTAINER.value],
            ],
            [
                "경제 분석을 얼마나 자주 읽거나 들으시나요?",
                ["자주 읽거나 듣는다.", 10, UserTypes.PROFESSIONALS.value],
                ["가끔 읽거나 듣는다.", 5, UserTypes.PROFESSIONALS.value],
                ["별로 읽거나 듣지 않는다.", 5, UserTypes.ENTERTAINER.value],
            ],
        ]

    async def get_questionnaire(self) -> List[UserTypeQuestionnaire]:
        questionnaires = set_user_type_questionnaire(self.questionnaire_data)
        return questionnaires

    async def create_user_type(
        self,
        answers: UserTypeQuestionnaireRequestDTO,
        session: AsyncSession,
    ) -> UserType:
        user_types = calculate_user_type(answers, self.questionnaire_data)
        return await UserTypeRepository().create(
            user_type=UserType(
                id=answers.id,
                user_type_issue_finder=user_types[UserTypes.ISSUE_FINDER.value],
                user_type_lifestyle_consumer=user_types[
                    UserTypes.LIFESTYLE_CONSUMER.value
                ],
                user_type_entertainer=user_types[UserTypes.ENTERTAINER.value],
                user_type_tech_specialist=user_types[UserTypes.TECH_SEPCIALIST.value],
                user_type_professionals=user_types[UserTypes.PROFESSIONALS.value],
            ),
            session=session,
        )

    async def get_user_type_by_id(self, id: int, session: AsyncSession) -> UserType:
        return await UserTypeRepository().get(pk=id, session=session)

    async def update_user_type(
        self, id: int, user_types: List[int], session: AsyncSession
    ) -> UserType:
        return await UserTypeRepository().update_user_type(
            id=id, user_types=user_types, session=session
        )

    async def get_all_user_types(self, session: AsyncSession) -> List[UserType]:
        return await UserTypeRepository().get_all(session=session)
