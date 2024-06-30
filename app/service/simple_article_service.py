from sqlalchemy.ext.asyncio import AsyncSession

from app.model.ai_client.ai_client import LLMModel
from app.model.ai_client.get_platform_client import get_platform_client
from app.model.prompt.prompt_version import PromptVersion, get_system_prompt
from app.service.crawl_article_service import CrawlArticleService
from app.utils.json_parser import parse


async def generate_simple_article(url: str, publisher: str, session: AsyncSession):
    ai_client = get_platform_client(LLMModel.GROQ_LLAMA_3)

    # 프롬프트를 가져온다.
    system_prompt = await get_system_prompt(version=PromptVersion.V_2024_06_30)
    print(system_prompt)

    # 크롤링한 기사를 가져온다.
    request_text = await CrawlArticleService().crawl_article(
        url=url, news_type=publisher, session=session
    )

    # AI에 요청한다.
    ai_result = await ai_client.request(
        request_text=request_text.content,
        system_prompt=system_prompt,
        assistant_prompt=None,
        model=LLMModel.GROQ_LLAMA_3,
    )

    return parse(ai_result)
