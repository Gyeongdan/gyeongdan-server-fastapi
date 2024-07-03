# newsletter_article_service.py

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

# 태윤이형이 만든 거 가져옴 해 보면서 안쓰는 거 제끼기
from app.model.ai_client.ai_client import LLMModel
from app.model.ai_client.get_platform_client import get_platform_client
from app.model.newsletter_article import NewsletterArticle
from app.model.prompt.prompt_version import PromptVersion, get_system_prompt
from app.model.subscription import MailTypeCategory
from app.repository.newsletter_article_crud import NewsletterArticleRepository

# 이건 쓸 수도


class NewsletterService:
    async def create_article(
        self, category: MailTypeCategory, content: str, session: AsyncSession
    ) -> NewsletterArticle:
        return await NewsletterArticleRepository().create(
            article_manager=NewsletterArticle(category=category.name, content=content),
            session=session,
        )

    async def get_content_by_id(
        self, id: int, session: AsyncSession
    ) -> NewsletterArticle:
        return await NewsletterArticleRepository().get_by_id(pk=id, session=session)

    async def get_all_contents(self, session: AsyncSession) -> List[NewsletterArticle]:
        return await NewsletterArticleRepository().get_all(session=session)

    async def get_content_by_category(
        self, category: MailTypeCategory, session: AsyncSession
    ) -> List[NewsletterArticle]:
        return await NewsletterArticleRepository().get_by_category(
            category=category, session=session
        )

    async def update_content(
        self, id: int, category: MailTypeCategory, content: str, session: AsyncSession
    ) -> NewsletterArticle:
        return await NewsletterArticleRepository().update_by_id(
            id=id, category=category, content=content, session=session
        )


async def generate_newsletter_article(session: AsyncSession):
    ai_client = get_platform_client(LLMModel.OPENAI_GPT4o)

    # 프롬프트
    system_prompt = await get_system_prompt(
        version=PromptVersion.newsletter_article_2024_07_03
    )

    ai_result = await ai_client.request(
        request_text="오늘의 뉴스",
        system_prompt=system_prompt,
        assistant_prompt=None,
        model=LLMModel.OPENAI_GPT4o,
    )

    # commit을 위해 잠시 쓰는 코드
    if session:
        print("쓰레기 코드")
    return ai_result
